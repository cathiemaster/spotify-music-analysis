# Analytics:
# Top 25 Artists
# Top 3 Genres
# Genre Frequency

from concurrent.futures import process
from contextlib import nullcontext
from datetime import datetime
import os
import spotipy
import spotipy.util as util
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
MAX_TRACKS = 50


def configure():
    load_dotenv()

    global CLIENT_ID, CLIENT_KEY, USERNAME
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_KEY = os.getenv("CLIENT_KEY")
    USERNAME = os.getenv("USERNAME")


def getOAuth(scope):
    auth = None
    try:
        token = util.prompt_for_user_token(
            username=USERNAME, client_id=CLIENT_ID, client_secret=CLIENT_KEY, redirect_uri=URI, scope=scope)
        if token:
            auth = spotipy.Spotify(auth=token)
        # mgr = SpotifyOAuth(
        #     client_id=CLIENT_ID, client_secret=CLIENT_KEY, redirect_uri=URI, scope=scope, open_browser=True)

        # auth = spotipy.Spotify(auth_manager=mgr)
    except SpotifyOauthError:
        print("ERROR: Unable to authenticate user")
        return auth

    return auth


def getClientAuth():
    auth = None
    try:
        auth = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID, client_secret=CLIENT_KEY))

    except SpotifyStateError:
        print("ERROR: Unable to create Client Auth")
        return (-1)

    return auth


def getAlbum(data):
    return data["track"]["album"]["name"]


def getTrack(data):
    return data["track"]["name"]


def getTrackId(data):
    return data["track"]["id"]


def getArtistData(data):
    artistList = data["track"]["artists"]

    if (len(artistList) > 0):
        return (artistList[0]["name"], artistList[0]["id"])

    return ("", "")


def getArtistTopGenre(artistId):
    sp = getClientAuth()
    artist = sp.artist(artistId)

    if (len(artist["genres"]) > 0):
        return artist["genres"][0]

    return ""


def getArtistAllGenres(artistId):
    sp = getClientAuth()
    artist = sp.artist(artistId)

    return artist["genres"]


def getTrackData(track):
    playedAt = track["played_at"]
    trackId = getTrackId(track)
    name = getTrack(track)
    album = getAlbum(track)
    (artist, artistId) = getArtistData(track)
    genre = getArtistTopGenre(artistId)

    return (
        trackId,
        playedAt,
        name,
        album,
        artist,
        artistId,
        album,
        genre
    )


def processArtistHistory(curr, track):
    playedAt = track["played_at"]
    trackId = getTrackId(track)

    for artist in track["track"]["artists"]:
        print(artist)
        artistName = artist["name"]
        artistId = artist["id"]

        # Push to artist_history db
        artistData = (
            playedAt,
            trackId,
            artistName,
            artistId
        )

        print(artistData)
        db.insertArtist(curr, artistData)

        # Push to genre_history db for all artist genres
        processGenreHistory(curr, playedAt, trackId, artistId)


def processGenreHistory(curr, playedAt, trackId, artistId):
    artistGenres = getArtistAllGenres(artistId)

    for genre in artistGenres:
        genreData = (
            playedAt,
            trackId,
            artistId,
            genre
        )
        print(genreData)
        db.insertGenre(curr, genreData)


def processTrackHistory(curr, tracks):
    for t in tracks:
        trackData = getTrackData(t)
        # print(trackData)
        # print()

        # Push to track_history db
        db.insertTrack(curr, trackData)

        processArtistHistory(curr, t)


def getRecentlyPlayed(sp, curr):
    limit = 50
    nextTimestamp = None
    group = 1

    print(f"Processing Group {group}...")

    res = sp.current_user_recently_played()
    processTrackHistory(res["items"])

    while (res["next"]) and (limit * group < MAX_TRACKS):
        group += 1
        nextTimestamp = res["cursors"]["before"]
        print(f"Processing Group {group}...")

        res = sp.current_user_recently_played(limit=limit, after=nextTimestamp)
        processTrackHistory(res["items"])


def main():
    configure()

    curr = db.connectToDB()
    db.getDBVersion(curr)

    sp = getOAuth(USER_READ_SCOPE)
    if (sp is not None):
        print("Getting recently played tracks...")
        getRecentlyPlayed(sp)

    db.closeDB(curr)


if __name__ == "__main__":
    main()
