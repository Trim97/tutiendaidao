import aiosqlite
from database import DB
import datetime

async def save_cultivation(player):

    today=str(datetime.date.today())

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT INTO cultivation_log
        VALUES (?,?,?,?)
        """,(today,player["level"],player["xp"],player["streak"]))

        await db.commit()

async def get_history(days=30):

    async with aiosqlite.connect(DB) as db:

        cursor=await db.execute("""
        SELECT * FROM cultivation_log
        ORDER BY date DESC
        LIMIT ?
        """,(days,))

        rows=await cursor.fetchall()

    return rows