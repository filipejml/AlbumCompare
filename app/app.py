import logging
import os
import re
from functools import wraps
from urllib.parse import urlparse, urljoin

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth_service import authenticate_user, create_user
from spotify_service import SpotifyAPIError, SpotifyClient, SpotifyConfigurationError
from track_comparison import compare_track_lists


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.json.ensure_ascii = False
app.secret_key = os.getenv("FLASK_SECRET_KEY", "altere-esta-chave-local")

SPOTIFY_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{22}$")
PLACEHOLDER_COVER = "https://placehold.co/300x300?text=Sem+capa"

spotify = SpotifyClient(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    market=os.getenv("SPOTIFY_MARKET", "BR"),
)


def is_authenticated():
    return bool(session.get("authenticated"))


def is_safe_redirect_url(target):
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ("http", "https") and host_url.netloc == redirect_url.netloc


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if app.config.get("LOGIN_DISABLED") or is_authenticated():
            return view(*args, **kwargs)
        if request.accept_mimetypes.best == "application/json":
            return json_error("Autenticação necessária.", 401)
        return redirect(url_for("login", next=request.full_path.rstrip("?")))

    return wrapped_view


def json_error(message, status_code):
    return jsonify({"error": message}), status_code


def valid_spotify_id(value):
    return bool(value and SPOTIFY_ID_PATTERN.fullmatch(value))


def track_summary(track):
    return {
        "id": track.get("id"),
        "name": track.get("name", "Faixa sem nome"),
        "preview_url": track.get("preview_url"),
    }


def album_details(album):
    images = album.get("images") or []
    external_urls = album.get("external_urls") or {}

    return {
        "name": album.get("name", "Álbum sem nome"),
        "release_date": album.get("release_date", "Não informada"),
        "total_tracks": album.get("total_tracks", 0),
        "popularity": album.get("popularity", 0),
        "external_url": external_urls.get("spotify"),
        "cover": images[0]["url"] if images and images[0].get("url") else PLACEHOLDER_COVER,
    }


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_authenticated():
        return redirect(url_for("index"))

    error_message = None
    next_url = request.args.get("next") or request.form.get("next") or url_for("index")
    if not is_safe_redirect_url(next_url):
        next_url = url_for("index")

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = authenticate_user(username, password)

        if user:
            session.clear()
            session["authenticated"] = True
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(next_url)

        error_message = "Usuário ou senha inválidos."

    return render_template("login.html", error_message=error_message, next_url=next_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_authenticated():
        return redirect(url_for("index"))

    error_message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        password_confirmation = request.form.get("password_confirmation", "")

        if password != password_confirmation:
            error_message = "A confirmação de senha não confere."
        else:
            try:
                user = create_user(username, password)
            except ValueError as error:
                error_message = str(error)
            else:
                flash(
                    f"Usuário {user['username']} cadastrado com sucesso. Faça login para continuar.",
                    "success",
                )
                return redirect(url_for("login"))

    return render_template("register.html", error_message=error_message)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/search_artist")
@login_required
def search_artist_route():
    query = (request.args.get("query") or "").strip()

    if len(query) < 3:
        return json_error("Digite pelo menos 3 caracteres para pesquisar.", 400)
    if len(query) > 100:
        return json_error("A pesquisa deve ter no máximo 100 caracteres.", 400)

    try:
        return jsonify({"artists": spotify.search_artists(query)})
    except SpotifyConfigurationError as error:
        logger.error("Configuração inválida do Spotify: %s", error)
        return json_error(str(error), 503)
    except SpotifyAPIError as error:
        logger.warning("Falha ao pesquisar artistas: %s", error)
        return json_error(error.public_message, error.status_code)


@app.route("/get_albums")
@login_required
def get_albums_route():
    artist_id = (request.args.get("artist_id") or "").strip()

    if not valid_spotify_id(artist_id):
        return json_error("Identificador de artista inválido.", 400)

    try:
        return jsonify({"albums": spotify.get_artist_albums(artist_id)})
    except SpotifyConfigurationError as error:
        logger.error("Configuração inválida do Spotify: %s", error)
        return json_error(str(error), 503)
    except SpotifyAPIError as error:
        logger.warning("Falha ao buscar álbuns: %s", error)
        return json_error(error.public_message, error.status_code)


@app.route("/compare", methods=["POST"])
@login_required
def compare():
    album1_id = (request.form.get("album1") or "").strip()
    album2_id = (request.form.get("album2") or "").strip()

    if not valid_spotify_id(album1_id) or not valid_spotify_id(album2_id):
        return render_template(
            "error.html",
            message="Selecione dois álbuns válidos para realizar a comparação.",
        ), 400

    if album1_id == album2_id:
        return render_template(
            "error.html",
            message="Selecione dois álbuns diferentes para realizar a comparação.",
        ), 400

    try:
        album1_info = spotify.get_album(album1_id)
        album2_info = spotify.get_album(album2_id)
        album1_tracks = spotify.get_album_tracks(album1_id)
        album2_tracks = spotify.get_album_tracks(album2_id)
    except SpotifyConfigurationError as error:
        logger.error("Configuração inválida do Spotify: %s", error)
        return render_template("error.html", message=str(error)), 503
    except SpotifyAPIError as error:
        logger.warning("Falha ao comparar álbuns: %s", error)
        return render_template("error.html", message=error.public_message), error.status_code

    common_tracks, unique_to_album1, unique_to_album2 = compare_track_lists(
        album1_tracks,
        album2_tracks,
    )

    common_tracks = [track_summary(track) for track in common_tracks]
    unique_to_album1 = [track_summary(track) for track in unique_to_album1]
    unique_to_album2 = [track_summary(track) for track in unique_to_album2]

    album1 = album_details(album1_info)
    album2 = album_details(album2_info)

    return render_template(
        "results.html",
        common_tracks=common_tracks,
        unique_to_album1=unique_to_album1,
        unique_to_album2=unique_to_album2,
        album1_cover=album1.pop("cover"),
        album2_cover=album2.pop("cover"),
        album1_details=album1,
        album2_details=album2,
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", message="A página solicitada não foi encontrada."), 404


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Erro interno não tratado: %s", error)
    return render_template(
        "error.html",
        message="Ocorreu um erro inesperado. Tente novamente em alguns instantes.",
    ), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(debug=debug_mode)
