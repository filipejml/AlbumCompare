import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from spotify_service import (  # noqa: E402
    SpotifyAPIError,
    SpotifyClient,
    SpotifyConfigurationError,
)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class SpotifyClientTests(unittest.TestCase):
    def make_client(self, session=None, clock=None):
        return SpotifyClient(
            "client-id",
            "client-secret",
            market="BR",
            session=session or Mock(),
            clock=clock or Mock(return_value=100),
        )

    def test_missing_credentials_raise_configuration_error(self):
        client = SpotifyClient(None, None)

        with self.assertRaises(SpotifyConfigurationError):
            client.search_artists("Beatles")

    def test_invalid_market_raises_configuration_error(self):
        client = SpotifyClient("id", "secret", market="Brasil")

        with self.assertRaises(SpotifyConfigurationError):
            client.search_artists("Beatles")

    def test_access_token_is_reused_until_expiration(self):
        session = Mock()
        session.post.return_value = FakeResponse(
            200,
            {"access_token": "token-1", "expires_in": 3600},
        )
        client = self.make_client(session=session)

        self.assertEqual(client._get_access_token(), "token-1")
        self.assertEqual(client._get_access_token(), "token-1")
        session.post.assert_called_once()

    def test_artist_search_uses_query_params(self):
        session = Mock()
        session.post.return_value = FakeResponse(
            200,
            {"access_token": "token-1", "expires_in": 3600},
        )
        session.request.return_value = FakeResponse(
            200,
            {"artists": {"items": [{"id": "artist"}]}},
        )
        client = self.make_client(session=session)

        artists = client.search_artists("AC/DC")

        self.assertEqual(artists, [{"id": "artist"}])
        request_kwargs = session.request.call_args.kwargs
        self.assertEqual(
            request_kwargs["params"],
            {"q": "AC/DC", "type": "artist", "market": "BR", "limit": 10},
        )

    def test_artist_albums_use_current_page_limit_and_market(self):
        session = Mock()
        session.post.return_value = FakeResponse(
            200,
            {"access_token": "token-1", "expires_in": 3600},
        )
        session.request.return_value = FakeResponse(
            200,
            {"items": [], "next": None},
        )
        client = self.make_client(session=session)

        client.get_artist_albums("artist")

        request_kwargs = session.request.call_args.kwargs
        self.assertEqual(request_kwargs["params"]["limit"], 10)
        self.assertEqual(request_kwargs["params"]["market"], "BR")

    def test_album_tracks_follow_all_pages(self):
        session = Mock()
        session.post.return_value = FakeResponse(
            200,
            {"access_token": "token-1", "expires_in": 3600},
        )
        session.request.side_effect = [
            FakeResponse(
                200,
                {
                    "items": [{"name": "Faixa 1"}],
                    "next": "https://api.spotify.com/v1/albums/album/tracks?offset=1",
                },
            ),
            FakeResponse(
                200,
                {"items": [{"name": "Faixa 2"}], "next": None},
            ),
        ]
        client = self.make_client(session=session)

        tracks = client.get_album_tracks("album")

        self.assertEqual([track["name"] for track in tracks], ["Faixa 1", "Faixa 2"])
        self.assertEqual(session.request.call_count, 2)

    def test_unauthorized_response_refreshes_token_once(self):
        session = Mock()
        session.post.side_effect = [
            FakeResponse(200, {"access_token": "old", "expires_in": 3600}),
            FakeResponse(200, {"access_token": "new", "expires_in": 3600}),
        ]
        session.request.side_effect = [
            FakeResponse(401, {"error": {"message": "expired"}}),
            FakeResponse(200, {"artists": {"items": []}}),
        ]
        client = self.make_client(session=session)

        self.assertEqual(client.search_artists("Beatles"), [])
        self.assertEqual(session.post.call_count, 2)
        self.assertEqual(session.request.call_count, 2)

    def test_external_pagination_url_is_rejected(self):
        client = self.make_client()

        with self.assertRaises(SpotifyAPIError):
            client._safe_url("https://example.com/steal-token")

    def test_request_timeout_becomes_controlled_error(self):
        session = Mock()
        session.post.return_value = FakeResponse(
            200,
            {"access_token": "token-1", "expires_in": 3600},
        )
        session.request.side_effect = requests.Timeout("demorou")
        client = self.make_client(session=session)

        with self.assertRaises(SpotifyAPIError) as context:
            client.search_artists("Beatles")

        self.assertEqual(context.exception.status_code, 504)


if __name__ == "__main__":
    unittest.main()
