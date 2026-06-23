import threading
import time
from urllib.parse import urlparse

import requests


class SpotifyConfigurationError(RuntimeError):
    """Indica que as credenciais necessárias não foram configuradas."""


class SpotifyAPIError(RuntimeError):
    """Erro controlado ao acessar a API do Spotify."""

    def __init__(self, message, status_code=502, public_message=None):
        super().__init__(message)
        self.status_code = status_code
        self.public_message = public_message or (
            "Não foi possível consultar o Spotify agora. Tente novamente mais tarde."
        )


class SpotifyClient:
    API_BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id,
        client_secret,
        market="BR",
        timeout=10,
        session=None,
        clock=None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.market = market.upper().strip() if market else ""
        self.timeout = timeout
        self.session = session or requests.Session()
        self.clock = clock or time.monotonic
        self._access_token = None
        self._token_expires_at = 0
        self._token_lock = threading.Lock()

    def _validate_credentials(self):
        if not self.client_id or not self.client_secret:
            raise SpotifyConfigurationError(
                "As credenciais do Spotify não estão configuradas. "
                "Preencha SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no arquivo app/.env."
            )
        if len(self.market) != 2 or not self.market.isalpha():
            raise SpotifyConfigurationError(
                "SPOTIFY_MARKET deve ser um código de país com duas letras, como BR."
            )

    def _get_access_token(self, force_refresh=False):
        self._validate_credentials()

        if (
            not force_refresh
            and self._access_token
            and self.clock() < self._token_expires_at
        ):
            return self._access_token

        with self._token_lock:
            if (
                not force_refresh
                and self._access_token
                and self.clock() < self._token_expires_at
            ):
                return self._access_token

            try:
                response = self.session.post(
                    self.TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    auth=(self.client_id, self.client_secret),
                    timeout=self.timeout,
                )
            except requests.Timeout as error:
                raise SpotifyAPIError(
                    "Timeout ao obter token do Spotify.",
                    status_code=504,
                ) from error
            except requests.RequestException as error:
                raise SpotifyAPIError(
                    f"Falha de rede ao obter token do Spotify: {error}"
                ) from error

            payload = self._read_json(response)
            if response.status_code >= 400:
                raise SpotifyAPIError(
                    f"Spotify recusou a autenticação ({response.status_code}): {payload}",
                    status_code=502,
                    public_message=(
                        "Não foi possível autenticar no Spotify. "
                        "Verifique as credenciais configuradas."
                    ),
                )

            token = payload.get("access_token")
            if not token:
                raise SpotifyAPIError("Resposta de autenticação sem access_token.")

            try:
                expires_in = max(int(payload.get("expires_in", 3600)), 60)
            except (TypeError, ValueError) as error:
                raise SpotifyAPIError(
                    "Resposta de autenticação com expires_in inválido."
                ) from error
            self._access_token = token
            self._token_expires_at = self.clock() + expires_in - 30
            return token

    def _read_json(self, response):
        try:
            return response.json()
        except ValueError as error:
            raise SpotifyAPIError(
                f"Spotify retornou conteúdo inválido com status {response.status_code}."
            ) from error

    def _request(self, method, path_or_url, params=None, retry_auth=True):
        url = self._safe_url(path_or_url)
        token = self._get_access_token()

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )
        except requests.Timeout as error:
            raise SpotifyAPIError(
                f"Timeout ao acessar {url}.",
                status_code=504,
            ) from error
        except requests.RequestException as error:
            raise SpotifyAPIError(f"Falha de rede ao acessar {url}: {error}") from error

        if response.status_code == 401 and retry_auth:
            self._get_access_token(force_refresh=True)
            return self._request(method, path_or_url, params=params, retry_auth=False)

        payload = self._read_json(response)

        if response.status_code == 429:
            raise SpotifyAPIError(
                "Limite de requisições do Spotify atingido.",
                status_code=503,
                public_message=(
                    "O Spotify recebeu muitas solicitações. "
                    "Aguarde alguns instantes e tente novamente."
                ),
            )

        if response.status_code == 404:
            raise SpotifyAPIError(
                f"Recurso não encontrado no Spotify: {url}",
                status_code=404,
                public_message="O artista ou álbum solicitado não foi encontrado.",
            )

        if response.status_code >= 400:
            raise SpotifyAPIError(
                f"Erro do Spotify ({response.status_code}) em {url}: {payload}"
            )

        return payload

    def _safe_url(self, path_or_url):
        if path_or_url.startswith("http"):
            parsed = urlparse(path_or_url)
            if parsed.scheme != "https" or parsed.netloc != "api.spotify.com":
                raise SpotifyAPIError("URL de paginação inválida recebida do Spotify.")
            return path_or_url
        return f"{self.API_BASE_URL}/{path_or_url.lstrip('/')}"

    def _get_all_pages(self, path, params=None):
        items = []
        next_url = path
        next_params = params
        visited_urls = set()

        while next_url:
            if len(visited_urls) >= 100:
                raise SpotifyAPIError("Limite de páginas da API do Spotify excedido.")

            page_key = str(next_url)
            if page_key in visited_urls:
                raise SpotifyAPIError("O Spotify retornou uma paginação circular.")
            visited_urls.add(page_key)

            payload = self._request("GET", next_url, params=next_params)
            page_items = payload.get("items")
            if not isinstance(page_items, list):
                raise SpotifyAPIError("Resposta paginada do Spotify sem lista de itens.")
            items.extend(page_items)
            next_url = payload.get("next")
            next_params = None

        return items

    def search_artists(self, query, limit=10):
        payload = self._request(
            "GET",
            "search",
            params={
                "q": query,
                "type": "artist",
                "market": self.market,
                "limit": limit,
            },
        )
        artists = payload.get("artists", {}).get("items")
        if not isinstance(artists, list):
            raise SpotifyAPIError("Resposta de pesquisa sem lista de artistas.")
        return artists

    def get_artist_albums(self, artist_id):
        albums = self._get_all_pages(
            f"artists/{artist_id}/albums",
            params={
                "include_groups": "album,single,compilation",
                "limit": 10,
                "market": self.market,
            },
        )

        unique_albums = {}
        for album in albums:
            album_id = album.get("id")
            if album_id and album_id not in unique_albums:
                unique_albums[album_id] = album
        return list(unique_albums.values())

    def get_album(self, album_id):
        return self._request(
            "GET",
            f"albums/{album_id}",
            params={"market": self.market},
        )

    def get_album_tracks(self, album_id):
        return self._get_all_pages(
            f"albums/{album_id}/tracks",
            params={"limit": 50, "market": self.market},
        )
