import logging
import os
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from spotify_service import SpotifyAPIError, SpotifyClient, SpotifyConfigurationError


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.json.ensure_ascii = False

SPOTIFY_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{22}$")
PLACEHOLDER_COVER = "https://placehold.co/300x300?text=Sem+capa"

spotify = SpotifyClient(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    market=os.getenv("SPOTIFY_MARKET", "BR"),
)


def json_error(message, status_code):
    return jsonify({"error": message}), status_code


def valid_spotify_id(value):
    return bool(value and SPOTIFY_ID_PATTERN.fullmatch(value))


def track_summary(track):
    return {
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
def index():
    return render_template("index.html")


@app.route("/search_artist")
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

    album1_tracks_info = [track_summary(track) for track in album1_tracks]
    album2_tracks_info = [track_summary(track) for track in album2_tracks]

    album1_track_names = {track["name"] for track in album1_tracks_info}
    album2_track_names = {track["name"] for track in album2_tracks_info}

    common_tracks = [
        track for track in album1_tracks_info if track["name"] in album2_track_names
    ]
    unique_to_album1 = [
        track for track in album1_tracks_info if track["name"] not in album2_track_names
    ]
    unique_to_album2 = [
        track for track in album2_tracks_info if track["name"] not in album1_track_names
    ]

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
