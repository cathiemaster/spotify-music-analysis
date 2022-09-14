# Analytics:
# Top 25 Artists
# Top 3 Genres
# Genre Frequency

from concurrent.futures import process
from datetime import datetime
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyOauthError
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyStateError
from dotenv import load_dotenv
import db

URI = "http://localhost:8888"
USER_READ_SCOPE = "user-read-recently-played playlist-read-private"
CLIENT_ID = ""
CLIENT_KEY = ""
USERNAME = ""
MAX_TRACKS = 500


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

        #print(playedAt, id, artists, album, name)

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
    nextTimestamp = None
    group = 1

    print(f"Processing Group {group}...")
    res = sp.current_user_recently_played(limit=limit)
    data += processRecentlyPlayed(res["items"])

    while (res["next"]) and (limit * group < MAX_TRACKS):
        group += 1
        nextTimestamp = res["cursors"]["before"]
        print(f"Processing Group {group}...")

        res = sp.current_user_recently_played(limit=limit, after=nextTimestamp)
        data += processRecentlyPlayed(res["items"])

    print(len(data))
    return data


def main():
    configure()

    db.connectToDB()

    # sp = getOAuth(USER_READ_SCOPE)
    # print("Getting recently played tracks...")
    # data = getRecentlyPlayed(sp)

    # for d in data:
    #     print(d["datetime"])


if __name__ == "__main__":
    main()
