import sqlite3

conn = sqlite3.connect("cultivation.db", check_same_thread=False)

cursor = conn.cursor()

def init_db():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player(
        id INTEGER PRIMARY KEY,
        name TEXT,
        level INTEGER,
        xp INTEGER,
        streak INTEGER,
        A REAL,
        B REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        message TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS youtube_stats(
        subs INTEGER,
        views INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()