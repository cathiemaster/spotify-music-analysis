import configparser
from dataclasses import dataclass
from configparser import ConfigParser
import psycopg2 as pgs


def config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)

        for p in params:
            db[p[0]] = p[1]
    else:
        raise Exception(f"{section} not found in file {filename}")

    return db


def connectToDB():
    conn = None

    try:
        print("Connecting to database...")

        params = config()
        conn = pgs.connect(**params)

        return conn.cursor()

    except (Exception, pgs.DatabaseError) as e:
        print(e)
        return None


def closeDB(curr):
    if (curr):
        curr.close()
        print("Database connection closed.")


def getDBVersion(curr):
    curr.execute("SELECT version()")
    dbVersion = curr.fetchone()

    print(f"PostgreSQL version: {dbVersion[0]}")


def insertTrack(curr, trackData):
    print(trackData)

    try:
        print("Inserting track...")

        insertQuery = """ INSERT INTO track_history 
            (played_at, track_id, title, album, track_link, primary_artist, primary_genre) 
            VALUES (%s,%s,%s,%s,%s,%s,%s) """

        sampleData = ("2022-10-19 01:31:59",
                      "35r28RDot7nPE7y9K9H7l0", "Feeling Whitney", "Stoney (Deluxe)", "https://api.spotify.com/v1/tracks/0y60itmpH0aPKsFiGxmtnh", "Post Malone", "dfw rap")

        curr.execute(insertQuery, sampleData)
        curr.commit()
        count = curr.rowcount()

        print(f"Committed {count} rows")
    except (Exception, pgs.DatabaseError) as e:
        print(e)


def insertArtist(curr, artistData):
    try:
        print("Inserting artist...")

        insertQuery = """ INSERT INTO artist_history 
            (played_at, artist_id, artist_name, track_id) 
            VALUES (%s,%s,%s,%s) """

        sampleData = ("2022-10-19 01:31:59",
                      "246dkjvS1zLTtiykXe5h60", "Noah Cyrus", "6J2LdBN97cDWn0MLxYh9HB")

        curr.execute(insertQuery, sampleData)
        curr.commit()
        count = curr.rowCount()

        print(f"Committed {count} rows")
    except (Exception, pgs.DatabaseError) as e:
        print(e)


def insertGenre(curr, genreData):
    try:
        print("Inserting genre...")

        insertQuery = """ INSERT INTO genre_history 
            (played_at, genre_name, track_id, artist_id)
            VALUES (%s,%s,%s,%s) """

        sampleData = ("2022-10-19 01:31:59", "pop",
                      "6J2LdBN97cDWn0MLxYh9HB", "246dkjvS1zLTtiykXe5h60")

        curr.execute(insertQuery, sampleData)
        curr.commit()
        count = curr.rowCount()

        print(f"Committed {count} rows")
    except (Exception, pgs.DatabaseError) as e:
        print(e)
