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

    print("Inserting track...")


def insertArtist(curr, artistData):
    print("Inserting artist...")


def insertGenre(curr, genreData):
    print("Inserting genre...")


def linkArtistToGenre():
    print("linking artist and genre...")
