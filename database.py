import aiosqlite

DB="tutien.db"

async def init_db():

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
        id TEXT PRIMARY KEY,
        xp INTEGER,
        level INTEGER,
        A INTEGER,
        streak INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS cultivation_log(
        date TEXT,
        level INTEGER,
        xp INTEGER,
        streak INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS youtube_stats(
        date TEXT,
        subs INTEGER,
        views INTEGER
        )
        """)

        await db.commit()

