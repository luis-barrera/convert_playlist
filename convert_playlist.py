import os
import pickle
import json
from dotenv import dotenv_values

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError


class ConvertSpotifyPlaylist();
    # Load .env
    environment = dotenv_values(".env")
    # List of tracks on Spotify
    sp_tracks_list = []
    # Id of playlist, created by YouTube
    yt_playlist = ""
    # Spotify connection
    sp = Null
    # Youtube connection
    youtube = Null


    def connectSpotify(self):
        print("Connecting to Spotify")

        # Connect to spotify
        sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=environment["SPOTIFY_APP_CLIENT_ID"],
                    client_secret=environment["SPOTIFY_APP_CLIENT_SECRET"],
                    redirect_uri=environment["SPOTIFY_APP_REDIRECT_URI"],
                    scope="user-library-read"))

        return sp

    def getSpotifyPlaylist(self):
        print("Getting Spotify tracks") 

        # Get tracks on spotify playlist
        tracks_in_playlist = sp.playlist_tracks(environment["SPOTIFY_PLAYLIST_URL"])
    
        for idx, item in enumerate(tracks_in_playlist["items"]):
            track = item["track"]
            # Get track's name
            track_name = track["name"]
            # Get track's artist
            artist = track["artists"][0]["name"]
            # Adds to list
            sp_tracks_list.append([artist, track_name])

        return sp_tracks_list


    def connectYoutube(self):
        print("Connecting to YouTube")
        
        # Security
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        try:
            # Tries to open previous credentials
            with open('creds.pkl', 'rb') as creds_file:
                credentials = pickle.load(creds_file)
        except IOError:
            # Google API scope
            scopes = ["https://www.googleapis.com/auth/youtube"]
            client_secrets_file = environment["YOUTUBE_API_CLIENT_SECRETS_FILE"]

            # Opens browser
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_local_server(port=0)

            # Save credentials to file to reuse
            output = open('creds.pkl', 'wb')
            pickle.dump(credentials, output, -1)
            output.close()
        finally:
            api_service_name = "youtube"
            api_version = "v3"

            # Connect to Youtube
            youtube = googleapiclient.discovery.build(api_service_name, api_version,
                                                  credentials=credentials)

        return youtube
    

    def getYoutubePlaylist(self):
        playlist_name = environment["PLAYLIST_NAME"],

        print("Finding playlist in user library: ", playlist_name)

        get_playlists = youtube.playlists().list().execute()
        playlists = get_playlists["items"]

        for playlist in playlists:
            if playlist["snippet"]["title"] == playlist_name[0]:
                yt_playlist = playlist["id"]
                print("Playlist ID", yt_playlist)
                return yt_playlist

        # If no playlist not founded, create a new playlist
        print("Playlist not found. Creating YouTube playlist")
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

        yt_playlist = playlists_insert_response["id"]
        print("Playlist ID", yt_playlist)
        return yt_playlist


    def addTrackToYoutube(self):
        print("Adding tracks to YouTube playlist")

        # Iterate tracks
        for artist, track_name in sp_tracks_list:
            max_tries = 5
            retry_count = 0
            backoff_time = 1

            # Sometimes the API gives errors
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


    # Search for a track and add it to playlist
    def addTrackToPlaylist(self, artist, track_name):
        # Search using artist and track
        q_string = f"{artist} {track_name}",

        print("Searching track: ", q_string)
        # Send request to API
        search_response = youtube.search().list(
            part = "snippet",
            q = q_string,
            type = "video"
        ).execute()

        # From response, get the first result, and then its ID
        video_id = search_response["items"][0]["id"]["videoId"]

        print("Adding track to playlist: id ", video_id)

        # Send a resquest to add a track to the playlist
        add_track_to_playlist = youtube.playlistItems().insert(
            part = "snippet",
            body = dict(
                snippet = dict(
                    playlistId = yt_playlist,
                    resourceId = dict(
                        videoId = video_id,
                        kind = 'youtube#video'
                    ) 
                )
                
            )
        ).execute()

        return add_track_to_playlist

    
if __name__ == '__main__':
    converter = ConvertSpotifyPlaylist()
    converter.connectSpotify()
    converter.connectYoutube()
    converter.getSpotifyPlaylist()
    converter.getYoutubePlaylist()
    converter.addTrackToYoutube()

