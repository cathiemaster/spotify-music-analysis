# Analytics:
# Top 25 Artists
# Top 3 Genres
# Genre Frequency

from concurrent.futures import process
from datetime import datetime
import os
import spotipy
import psycopg2 as pgs
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyOauthError
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyStateError
from dotenv import load_dotenv

URI = "http://localhost:8888"
USER_READ_SCOPE = "user-read-recently-played playlist-read-private"
CLIENT_ID = ""
CLIENT_KEY = ""
USERNAME = ""


def configure():
    load_dotenv()

    global CLIENT_ID, CLIENT_KEY, USERNAME
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_KEY = os.getenv("CLIENT_KEY")
    USERNAME = os.getenv("USERNAME")


def getOAuth(scope):
    auth = None
    try:
        mgr = SpotifyOAuth(
            client_id=CLIENT_ID, client_secret=CLIENT_KEY, redirect_uri=URI, scope=scope)

        auth = spotipy.Spotify(auth_manager=mgr)
    except SpotifyOauthError:
        print("ERROR: Unable to authenticate user")
        return(-1)

    return auth


def getClientAuth():
    auth = None
    try:
        auth = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, client_secret=CLIENT_KEY))

    except SpotifyStateError:
        print("ERROR: Unable to create Client Auth")
        return(-1)

    return auth


def getAlbum(data):
    return data["track"]["album"]["name"]


def getTrack(data):
    return data["track"]["name"]


def getTrackId(data):
    return data["track"]["id"]


def getArtists(data):
    artistList = data["track"]["artists"]
    artists = []
    for a in artistList:
        genres = getArtistGenre(a["id"])
        artists.append(
            {"name": a["name"],
             "genres": genres})

    return artists


def getArtistGenre(artistId):
    sp = getClientAuth()
    artist = sp.artist(artistId)

    return artist["genres"]


def processRecentlyPlayed(tracks):
    data = []

    for t in tracks:
        playedAt = t["played_at"]
        id = getTrackId(t)
        artists = getArtists(t)
        album = getAlbum(t)
        name = getTrack(t)

        data.append({
            "datetime": playedAt,
            "id": id,
            "title": name,
            "artists": artists,
            "album": album,
        })

    return data


def getRecentlyPlayed(sp):
    data = []
    limit = 50
    before = None

    res = sp.current_user_recently_played(limit=limit)
    data += processRecentlyPlayed(res["items"])
    print(data)

    # while res["next"]:
    #     before = res["cursors"]["before"]

    #     res = sp.current_user_recently_played(limit=limit)
    #     data += processRecentlyPlayed(res["items"])


def main():
    configure()

    sp = getOAuth(USER_READ_SCOPE)
    getRecentlyPlayed(sp)
    # res = sp.current_user_recently_played()

    # print(res["next"], res["limit"], res["cursors"])


if __name__ == "__main__":
    main()
