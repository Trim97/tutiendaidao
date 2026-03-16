from youtube_scanner import scan
from cultivation import get_player
from database import cursor

async def nightly_report(context):

    xp,event=scan()

    p=get_player()

    cursor.execute(
        "SELECT value FROM settings WHERE key='chat_id'"
    )

    row=cursor.fetchone()

    if not row:
        return

    chat_id=row[0]

    msg=f"""
📜 Báo cáo tu luyện

⚔️ Level: {p[2]}
✨ XP: {p[3]}

🎥 XP YouTube hôm nay:
{xp}
"""

    if event:
        msg+=f"\n{event} xuất hiện!"

    await context.bot.send_message(
        chat_id=chat_id,
        text=msg
    )