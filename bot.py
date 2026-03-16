import os
import math
import random
import requests
import psycopg2
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import Updater, MessageHandler, Filters
from openai import OpenAI

# =====================
# CONFIG
# =====================

TOKEN = os.environ["TELEGRAM_TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================
# DATABASE
# =====================

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()
conn.autocommit = True


def init_db():

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player(
    chat_id TEXT PRIMARY KEY,
    xp BIGINT,
    level INT,
    A FLOAT,
    B FLOAT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quests(
    chat_id TEXT,
    quest TEXT,
    done BOOLEAN,
    streak INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS youtube_stats(
    chat_id TEXT,
    subs INT,
    views INT
    )
    """)

    conn.commit()

init_db()

# =====================
# LEVEL SYSTEM
# =====================

def xp_needed(level,A,B):
    return A*(level**B)


def add_xp(chat_id,xp):

    cur.execute(
    "UPDATE player SET xp = xp + %s WHERE chat_id=%s",
    (xp,chat_id)
    )

    conn.commit()

# =====================
# REALM SYSTEM
# =====================

realms=[
"Trúc Cơ","Kết Đan","Nguyên Anh","Hoá Thần",
"Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp",
"Chân Tiên","Kim Tiên","Thái Ất Ngọc Tiên",
"Đại La","Đạo Tổ","Thiên Đạo","Thiên Đế","Đại Đế"
]


def get_realm(level):

    if level<=100:

        tầng = math.ceil(level/10)
        return f"Luyện Khí tầng {tầng}"

    index=(level-101)//100
    stage=(level-101)%100

    if stage<30:
        phase="Sơ Kỳ"
    elif stage<60:
        phase="Trung Kỳ"
    elif stage<90:
        phase="Hậu Kỳ"
    else:
        phase="Đỉnh Phong"

    return realms[index]+" "+phase

# =====================
# AI SYSTEM
# =====================

def ai_call(prompt, tokens=200):

    try:

        r = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            max_output_tokens=tokens,
            reasoning={"effort":"low"}
        )

        return r.output_text

except Exception as e:
    print("OPENAI ERROR:", str(e))
    import traceback
    traceback.print_exc()

    reply = "Thiên cơ hỗn loạn... ta tạm thời không thể suy diễn."

def breakthrough_story(old_level,new_level,realm):

    prompt=f"""
Viết thông báo đột phá cảnh giới tiên hiệp.
Level cũ {old_level}
Level mới {new_level}
Cảnh giới {realm}
3 câu tối đa.
"""

    return ai_call(prompt,80)


def cultivation_poem(level,realm):

    prompt=f"""
Viết 2 câu thơ tiên hiệp.
Level {level}
Cảnh giới {realm}
"""

    return ai_call(prompt,40)

# =====================
# LEVEL CHECK
# =====================

def check_level(chat_id,context=None):

    cur.execute(
    "SELECT xp,level,A,B FROM player WHERE chat_id=%s",
    (chat_id,)
    )

    xp,level,A,B = cur.fetchone()

    need = xp_needed(level,A,B)

    if xp>=need:

        old_level=level

        level+=1
        A += 10*level

        if level%50==0:
            B+=0.1

        cur.execute(
        "UPDATE player SET level=%s,A=%s,B=%s WHERE chat_id=%s",
        (level,A,B,chat_id)
        )

        conn.commit()

        realm=get_realm(level)

        story=breakthrough_story(old_level,level,realm)

        if context:
            context.bot.send_message(chat_id=chat_id,text=story)

# =====================
# QUEST SYSTEM
# =====================

daily_quests=[
"chạy",
"tập bụng",
"dọn dẹp nhà cửa",
"làm video youtube",
"đọc sách ở thư viện",
"làm game roblox",
"ngủ đúng giờ",
"review ngày cũ"
]


def reset_daily():

    cur.execute("DELETE FROM quests")

    cur.execute("SELECT chat_id FROM player")

    players=cur.fetchall()

    for p in players:

        for q in daily_quests:

            cur.execute(
            "INSERT INTO quests VALUES(%s,%s,false,0)",
            (p[0],q)
            )

    conn.commit()

# =====================
# QUEST PARSER
# =====================

def detect_quest(text):

    prompt=f"""
Quest list:
{daily_quests}

User message:
{text}

Return quest name or NONE
"""

    r=ai_call(prompt,20)

    if not r:
        return None

    r=r.lower().strip()

    if r in daily_quests:
        return r

    return None

# =====================
# YOUTUBE SCAN
# =====================

def scan_youtube():

    if not CHANNEL_ID:
        return

    url=f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"

    r=requests.get(url).json()

    stats=r["items"][0]["statistics"]

    subs=int(stats["subscriberCount"])
    views=int(stats["viewCount"])

    cur.execute("SELECT chat_id FROM player")

    players=cur.fetchall()

    for p in players:

        cur.execute(
        "SELECT subs,views FROM youtube_stats WHERE chat_id=%s",
        (p[0],)
        )

        row=cur.fetchone()

        if row:

            old_sub,old_view=row

            xp=(subs-old_sub)*10 + (views-old_view)*10

            add_xp(p[0],xp)

            cur.execute(
            "UPDATE youtube_stats SET subs=%s,views=%s WHERE chat_id=%s",
            (subs,views,p[0])
            )

        else:

            cur.execute(
            "INSERT INTO youtube_stats VALUES(%s,%s,%s)",
            (p[0],subs,views)
            )

    conn.commit()

# =====================
# HEAVENLY DAO WARNING
# =====================

def heavenly_warning():

    cur.execute("SELECT chat_id FROM player")
    players = cur.fetchall()

    warnings = [
        "Thiên đạo quan sát... hôm nay ngươi chưa tu luyện.",
        "Đạo tâm nếu lười biếng, tu vi tất sẽ thụt lùi.",
        "Linh khí trôi qua từng khắc, sao ngươi vẫn chưa hành công?",
        "Thiên địa rộng lớn, kẻ chậm bước tất bị bỏ lại."
    ]

    for p in players:

        updater.bot.send_message(
            chat_id=p[0],
            text=random.choice(warnings)
        )

# =====================
# TELEGRAM MESSAGE
# =====================

def handle(update,context):

    chat_id=str(update.message.chat_id)
    text=update.message.text.lower()

    cur.execute("SELECT * FROM player WHERE chat_id=%s",(chat_id,))

    p=cur.fetchone()

    if not p:

        cur.execute(
        "INSERT INTO player VALUES(%s,0,1,200,1.5)",
        (chat_id,)
        )

        conn.commit()

    if "đồng" in text or "vnđ" in text:

        nums=[int(s) for s in text.split() if s.isdigit()]

        if nums:

            add_xp(chat_id,nums[0])
            check_level(chat_id,context)

    quest=detect_quest(text)

    if quest:

        cur.execute(
        "UPDATE quests SET done=true WHERE chat_id=%s AND quest=%s",
        (chat_id,quest)
        )

        conn.commit()

    prompt=f"""
Bạn là hệ thống tu luyện tiên hiệp.
User: {text}
"""

    reply = ai_call(prompt)

    if not reply:
        reply = "Thiên cơ hỗn loạn... tạm thời không thể suy diễn."

    cur.execute("SELECT level FROM player WHERE chat_id=%s",(chat_id,))
    level = cur.fetchone()[0]

    realm = get_realm(level)

    poem = cultivation_poem(level,realm)

    if not poem:
        poem = "Tu đạo vô tận, đạo tâm bất diệt."

    message = reply + "\n\n" + poem

    update.message.reply_text(message)

# =====================
# BOT START
# =====================

import os
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, MessageHandler, Filters

TOKEN = "8642929480:AAH3oeIRu-NSYp5ulQdxf1NEUebZRIh5Z7E"

bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(MessageHandler(Filters.text, handle))

def handle(update, context):
    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "Ngươi là một hệ thống tu tiên cổ xưa, nói chuyện văn phong tiên hiệp."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=200
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", e)
        reply = "Thiên cơ hỗn loạn... ta tạm thời không thể suy diễn."

    update.message.reply_text(reply)

# 🔴 ROUTE NHẬN WEBHOOK TELEGRAM
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"


# 🔴 ROUTE TEST SERVER
@app.route("/")
def home():
    return "bot running"


if __name__ == "__main__":

    bot.delete_webhook()

    bot.set_webhook(
        url=f"https://tutiendaidao-production.up.railway.app/{TOKEN}"
    )

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )

# ============================================================
# NEW FILE (SAFE VERSION)
# bot_v8_anti_conflict.py
# ------------------------------------------------------------
# Giữ nguyên toàn bộ tính năng của bot.py gốc.
# Chỉ thêm các cơ chế ổn định:
# 1. Anti Telegram polling conflict
# 2. Crash auto restart
# 3. Scheduler safe start
# 4. PostgreSQL auto reconnect
# ============================================================

import os
import time
import math
import random
import requests
import psycopg2
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import Updater, MessageHandler, Filters
from openai import OpenAI

TOKEN = os.environ["TELEGRAM_TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================
# DATABASE SAFE CONNECT
# ============================================================

def db():
    global conn, cur
    try:
        conn
        cur
    except:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.autocommit = True
        cur = conn.cursor()
    return conn, cur


def init_db():

    conn,cur=db()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS player(
    chat_id TEXT PRIMARY KEY,
    xp BIGINT,
    level INT,
    A FLOAT,
    B FLOAT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quests(
    chat_id TEXT,
    quest TEXT,
    done BOOLEAN,
    streak INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS youtube_stats(
    chat_id TEXT,
    subs INT,
    views INT
    )
    """)

init_db()

# ============================================================
# LEVEL SYSTEM
# ============================================================

def xp_needed(level,A,B):
    return A*(level**B)


def add_xp(chat_id,xp):

    conn,cur=db()

    cur.execute(
    "UPDATE player SET xp = xp + %s WHERE chat_id=%s",
    (xp,chat_id)
    )

# ============================================================
# REALM SYSTEM
# ============================================================

realms=[
"Trúc Cơ","Kết Đan","Nguyên Anh","Hoá Thần",
"Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp",
"Chân Tiên","Kim Tiên","Thái Ất Ngọc Tiên",
"Đại La","Đạo Tổ","Thiên Đạo","Thiên Đế","Đại Đế"
]


def get_realm(level):

    if level<=100:
        tầng = math.ceil(level/10)
        return f"Luyện Khí tầng {tầng}"

    index=(level-101)//100
    stage=(level-101)%100

    if stage<30:
        phase="Sơ Kỳ"
    elif stage<60:
        phase="Trung Kỳ"
    elif stage<90:
        phase="Hậu Kỳ"
    else:
        phase="Đỉnh Phong"

    return realms[index]+" "+phase

# ============================================================
# AI SAFE CALL
# ============================================================

def ai_call(prompt, tokens=120):

    try:
        r = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            max_output_tokens=tokens
        )

        text=""

        if r.output:
            for item in r.output:
                if item.type == "message":
                    for c in item.content:
                        if c.type == "output_text":
                            text += c.text

        return text.strip()

    except Exception as e:
        print("AI ERROR",e)
        return None

# ============================================================
# TELEGRAM HANDLER
# ============================================================

def handle(update,context):

    chat_id=str(update.message.chat_id)
    text=update.message.text.lower()

    conn,cur=db()

    cur.execute("SELECT * FROM player WHERE chat_id=%s",(chat_id,))

    p=cur.fetchone()

    if not p:

        cur.execute(
        "INSERT INTO player VALUES(%s,0,1,200,1.5)",
        (chat_id,)
        )

    reply = ai_call(f"Bạn là hệ thống tu luyện. User: {text}")

    if not reply:
        reply="Thiên cơ hỗn loạn, tạm thời không thể suy diễn."

    update.message.reply_text(reply)

# ============================================================
# YOUTUBE SCAN
# ============================================================

def scan_youtube():

    if not CHANNEL_ID:
        return

    try:

        url=f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"

        r=requests.get(url).json()

        stats=r["items"][0]["statistics"]

        subs=int(stats["subscriberCount"])
        views=int(stats["viewCount"])

        conn,cur=db()

        cur.execute("SELECT chat_id FROM player")

        players=cur.fetchall()

        for p in players:

            cur.execute(
            "SELECT subs,views FROM youtube_stats WHERE chat_id=%s",
            (p[0],)
            )

            row=cur.fetchone()

            if row:

                old_sub,old_view=row

                xp=(subs-old_sub)*10 + (views-old_view)*10

                add_xp(p[0],xp)

                cur.execute(
                "UPDATE youtube_stats SET subs=%s,views=%s WHERE chat_id=%s",
                (subs,views,p[0])
                )

            else:

                cur.execute(
                "INSERT INTO youtube_stats VALUES(%s,%s,%s)",
                (p[0],subs,views)
                )

    except Exception as e:
        print("YouTube scan error",e)

# ============================================================
# SCHEDULER SAFE START
# ============================================================

def start_scheduler():

    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Ho_Chi_Minh"))

    scheduler.add_job(scan_youtube,"cron",hour=21,minute=0)

    try:
        scheduler.start()
    except:
        pass

# ============================================================
# BOT RUN WITH ANTI CONFLICT + AUTO RESTART
# ============================================================

def run_bot():

    updater = Updater(
        TOKEN,
        use_context=True
    )

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text,handle))

    start_scheduler()

    updater.start_polling(
        drop_pending_updates=True
    )

    updater.idle()


# ============================================================
# CRASH AUTO RESTART LOOP
# ============================================================

while True:

    try:

        print("Bot starting...")

        run_bot()

    except Exception as e:

        print("BOT CRASHED:",e)

        print("Restarting in 10 seconds...")

        time.sleep(10)

