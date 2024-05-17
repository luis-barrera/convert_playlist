# Convert playlists from Spotify to Youtube #

Little script used by me to easily transfer(convert) playlist in Spotify to Youtube.

## Libreries ##

These are the main libraries used in this project:

- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [spotipy](https://spotipy.readthedocs.io/)
- [google-api-python-client](https://github.com/googleapis/google-api-python-client)

The complete list is in `requirements.txt` file.

## Installation and usage ##

1. Clone project:

```shell
git clone https://github.com/luis-barrera/convert_playlist.git
```

2. Change directory and make a virtualenv(`venv`):

```shell
cd mkdir && python -m venv venv
```

3. Activate `venv` (may vary upon different shells, like fish):

```shell
source venv/bin/activate
```

4. Installs dependencies:

```shell
pip install -r requirements.txt
```

5. Generate and enviroment file with your secrets:

```shell
touch .env
```

6. Open enviroment file and add next:

```
SPOTIFY_APP_CLIENT_ID=#1
SPOTIFY_APP_CLIENT_SECRET=#2
SPOTIFY_APP_REDIRECT_URI=#3
SPOTIFY_PLAYLIST_URL=#4
YOUTUBE_API_CLIENT_SECRETS_FILE=#5
PLAYLIST_NAME=#6
```
    
Replace the next values:

- For #1 #2 #3 you have to get it from [Spotify Developer Console](https://developer.spotify.com/), use this [video](https://www.youtube.com/watch?v=kaBVN8uP358) as tutorial. Thanks to Spotipy people for the tutorial.
- For #4, go to your spotify app (desktop, mobile, fridge, idk...) and copy the URL that gives you when click on "Share".
- For #5, you have to create an Google Developer Account and get access to Youtube Data API v3, use this [tutorial](https://www.youtube.com/watch?v=I5ili_1G0Vk)(I don't own this content, credits to Jie Jenn's channel) as example.
- For #6, is the name you want to for the Youtube Playlist. Be careful, don't use especial characters in the name, can give some errors.

7. Run the script, some browser windows will open asking for permissions to your Spotify and Youtube accounts:

```shell
python convert_playlist.py
```

## Problems and solution ##

- One problem that made me spent a lot of time trying to figure it out is that Youtube can give some errors when using special characters in the playlist name.
- Also, it takes times to understand how Google APIs (in general) works.
