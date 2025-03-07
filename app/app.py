from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from math import ceil

load_dotenv()

app = Flask(__name__)

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Get Spotify API token
def get_spotify_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

# Search for artist
def search_artist(query, token):
    url = f'https://api.spotify.com/v1/search?q={query}&type=artist'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

# Get artist albums
def get_artist_albums(artist_id, token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

# Get album tracks
def get_album_tracks(album_id, token):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_artist')
def search_artist_route():
    query = request.args.get('query')
    token = get_spotify_token()
    results = search_artist(query, token)
    artists = results['artists']['items']
    return {'artists': artists}

@app.route('/get_albums')
def get_albums_route():
    artist_id = request.args.get('artist_id')
    token = get_spotify_token()
    albums = get_artist_albums(artist_id, token)
    return {'albums': albums['items']}

@app.route('/compare', methods=['POST'])
def compare():
    album1_id = request.form['album1']
    album2_id = request.form['album2']
    token = get_spotify_token()

    # Obter informações detalhadas dos álbuns
    album1_info = requests.get(f'https://api.spotify.com/v1/albums/{album1_id}', headers={'Authorization': f'Bearer {token}'}).json()
    album2_info = requests.get(f'https://api.spotify.com/v1/albums/{album2_id}', headers={'Authorization': f'Bearer {token}'}).json()

    # Obter as músicas de cada álbum
    album1_tracks = get_album_tracks(album1_id, token)
    album2_tracks = get_album_tracks(album2_id, token)

    # Extrair nomes e preview_url das músicas
    album1_tracks_info = [{'name': track['name'], 'preview_url': track['preview_url']} for track in album1_tracks['items']]
    album2_tracks_info = [{'name': track['name'], 'preview_url': track['preview_url']} for track in album2_tracks['items']]

    # Comparar músicas
    album1_track_names = {track['name'] for track in album1_tracks_info}
    album2_track_names = {track['name'] for track in album2_tracks_info}

    common_tracks = [track for track in album1_tracks_info if track['name'] in album2_track_names]
    unique_to_album1 = [track for track in album1_tracks_info if track['name'] not in album2_track_names]
    unique_to_album2 = [track for track in album2_tracks_info if track['name'] not in album1_track_names]

    # URLs das capas dos álbuns
    album1_cover = album1_info['images'][0]['url'] if album1_info['images'] else 'https://via.placeholder.com/150'
    album2_cover = album2_info['images'][0]['url'] if album2_info['images'] else 'https://via.placeholder.com/150'

    # Informações detalhadas dos álbuns
    album1_details = {
        'name': album1_info['name'],
        'release_date': album1_info['release_date'],
        'total_tracks': album1_info['total_tracks'],
        'popularity': album1_info['popularity'],
        'external_url': album1_info['external_urls']['spotify']
    }
    album2_details = {
        'name': album2_info['name'],
        'release_date': album2_info['release_date'],
        'total_tracks': album2_info['total_tracks'],
        'popularity': album2_info['popularity'],
        'external_url': album2_info['external_urls']['spotify']
    }

    return render_template('results.html', 
                          common_tracks=common_tracks, 
                          unique_to_album1=unique_to_album1, 
                          unique_to_album2=unique_to_album2,
                          album1_cover=album1_cover,
                          album2_cover=album2_cover,
                          album1_details=album1_details,
                          album2_details=album2_details)
    
if __name__ == '__main__':
    app.run(debug=True)