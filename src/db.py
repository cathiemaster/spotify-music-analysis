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

        cur = conn.cursor()
        cur.execute("SELECT version()")
        dbVersion = cur.fetchone()
        print(f"PostgreSQL version: {dbVersion[0]}")

        cur.close()

    except (Exception, pgs.DatabaseError) as e:
        print(e)

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")
