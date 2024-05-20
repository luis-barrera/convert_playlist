import os
import pickle
import json
import time
from dotenv import dotenv_values

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from ytmusicapi import YTMusic

class ConvertSpotifyPlaylist():
    # Load .env
    environment = dotenv_values(".env")
    # List of tracks on Spotify
    sp_tracks_list = []
    # Id of playlist, created by YouTube
    yt_playlist = ""
    # Spotify connection
    sp = ""
    # Youtube connection
    youtube = ""
    # File containing tracks not found
    not_found_txt = open("not_found.txt", "wt")


    def connectSpotify(self):
        print("Connecting to Spotify")

        # Connect to spotify
        self.sp = spotipy.Spotify(
                auth_manager = SpotifyOAuth(
                    client_id = self.environment["SPOTIFY_APP_CLIENT_ID"],
                    client_secret = self.environment["SPOTIFY_APP_CLIENT_SECRET"],
                    redirect_uri = self.environment["SPOTIFY_APP_REDIRECT_URI"],
                    scope="user-library-read"))

        return self.sp

    def getSpotifyPlaylist(self):
        print("Getting Spotify tracks") 

        page = 0
        my_limit = 50
        do_while = True

        while do_while:
            # Get tracks on spotify playlist
            tracks_in_playlist = self.sp.playlist_tracks(self.environment["SPOTIFY_PLAYLIST_URL"], limit = my_limit, offset = page * my_limit)

            for idx, item in enumerate(tracks_in_playlist["items"]):
                track = item["track"]
                # Get track's name
                track_name = track["name"]
                # Get track's artist
                artist = track["artists"][0]["name"]
                # Adds to list
                self.sp_tracks_list.append([artist, track_name])

            page += 1
            do_while = len(tracks_in_playlist["items"]) == my_limit
        
        return self.sp_tracks_list


    def connectYoutube(self):
        print("Connecting to YouTube")
        
        self.youtube = YTMusic("oauth.json")

        return self.youtube
    

    def getYoutubePlaylist(self):
        playlist_name = self.environment["PLAYLIST_NAME"],

        print("Finding playlist in user library: ", playlist_name[0])


        self.yt_playlist = self.youtube.create_playlist(playlist_name[0], "Playlist creted using script")
        print("Playlist ID", self.yt_playlist)
        return self.yt_playlist


    def addTrackToYoutube(self):
        print("Adding tracks to YouTube playlist")

        # Iterate tracks
        for artist, track_name in self.sp_tracks_list:
            self.addTrackToPlaylist(artist, track_name)

        self.not_found_txt.close()


    # Search for a track and add it to playlist
    def addTrackToPlaylist(self, artist, track_name):
        # Search using artist and track
        q_string = f"{artist} {track_name}",

        print("Searching track: ", q_string[0])
        # Send request to API
        search_results = self.youtube.search(q_string[0])

        try:
            # From response, get the first result, and then its ID
            video_id = search_results[0]["videoId"]

            print("Adding track to playlist: id ", video_id)

            # Send a resquest to add a track to the playlist
            if video_id:
                add_track_to_playlist = self.youtube.add_playlist_items(self.yt_playlist, [video_id])
            else:
                raise Exception("video_id is empty")
        except Exception as e:
            print("Error trying to add track", q_string[0])
            self.not_found_txt.write(q_string[0] + "\n")
    
if __name__ == '__main__':
    converter = ConvertSpotifyPlaylist()
    converter.connectSpotify()
    converter.connectYoutube()
    converter.getSpotifyPlaylist()
    converter.getYoutubePlaylist()
    converter.addTrackToYoutube()

