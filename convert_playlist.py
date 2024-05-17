from dotenv import dotenv_values
import os
import pickle
import json

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError

# Load .env
environment = dotenv_values(".env")

def addTrackToPlaylist(artist, track_name):
    q_string = f"{artist} {track_name}",
    search_response = youtube.search().list(
        part="snippet",
        q = q_string,
        type="video"
    ).execute()

    video_id = search_response["items"][0]["id"]["videoId"]
    print(video_id)

    add_track_to_playlist = youtube.playlistItems().insert(
            part = "snippet",
            body = dict(
              snippet = dict(
                playlistId = id_playlist,
                resourceId = dict(
                    videoId = video_id,
                    kind = 'youtube#video'
                ) 
            )
            
        )
    ).execute()


# List of tracks
tracks_list = []

print("Connecting to Spotify")
# Connect to spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=environment["SPOTIFY_APP_CLIENT_ID"],
                                               client_secret=environment["SPOTIFY_APP_CLIENT_SECRET"],
                                               redirect_uri=environment["SPOTIFY_APP_REDIRECT_URI"],
                                               scope="user-library-read"))


print("Getting Spotify tracks") 
## Get tracks on playlist
tracks_in_playlist = sp.playlist_tracks(environment["SPOTIFY_PLAYLIST_URL"])
for idx, item in enumerate(tracks_in_playlist["items"]):
    track = item["track"]
    # Get track's name
    track_name = track["name"]
    # Get track's artist
    artist = track["artists"][0]["name"]
    # Adds to list
    tracks_list.append([artist, track_name])


print("Connecting to YouTube")
# Security
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

try:
    # Credentials file
    with open('creds.pkl', 'rb') as creds_file:
        credentials = pickle.load(creds_file)
except IOError:
    # Google API scope
    scopes = ["https://www.googleapis.com/auth/youtube"]
    client_secrets_file = environment["YOUTUBE_API_CLIENT_SECRETS_FILE"]

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)

    output = open('creds.pkl', 'wb')
    pickle.dump(credentials, output, -1)
    output.close()
finally:
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version,
                                          credentials=credentials)
    

print("Creating YouTube playlist")
playlist_name = environment["PLAYLIST_NAME"],
playlists_insert_response = youtube.playlists().insert(
    part = "snippet,status",
    body = dict(
        snippet = dict(
            title = playlist_name[0],
            description = "Playlist importada de Spotify"
        ),
        status = dict(
            privacyStatus = "private"
        )
    )
).execute()

id_playlist = playlists_insert_response["id"]
print(id_playlist)

print("Adding tracks to YouTube playlist")
for artist, track_name in tracks_list:
    max_tries = 5
    retry_count = 0
    backoff_time = 1

    while retry_count < max_tries:
        try:
            addTrackToPlaylist(artist, track_name)
            retry_count = max_tries
        except HttpError as e:
            if e.resp.status == 409 and 'SERVICE_UNAVAILABLE' in str(e):
                retry_count += 1
                print(f"Attempt {retry_count} failed. Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                # Exponential backoff
                backoff_time *= 2
            else:
                raise Exception("Failed to add the song to the playlist after multiple retries.")
    

print("Finish")
