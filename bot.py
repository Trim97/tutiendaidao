import os
import json
import math
import random
import datetime

from telegram import Update
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
ContextTypes
)

from openai import OpenAI

# ========================
# CONFIG
# ========================

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

DATA_FILE = "players.json"

# ========================
# QUEST LIST
# ========================

QUESTS = [
"Chạy",
"Tập bụng",
"Dọn dẹp nhà cửa",
"Làm video youtube",
"Đọc sách ở thư viện",
"Làm game roblox",
"Ngủ đúng giờ",
"Review ngày"
]

# ========================
# EVENTS
# ========================

EVENTS = [
"Ngươi gặp một lão giả bí ẩn truyền công (+150 XP)",
"Ngộ đạo dưới cổ thụ (+1 streak)",
"Tâm ma xuất hiện (A +5)",
"Khám phá bí cảnh (+200 XP)",
"Không có dị tượng hôm nay"
]

# ========================
# DATA
# ========================

players = {}

def load_data():
    global players
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r") as f:
            players=json.load(f)

def save_data():
    with open(DATA_FILE,"w") as f:
        json.dump(players,f)

# ========================
# PLAYER
# ========================

def get_player(uid):

    uid=str(uid)

    if uid not in players:

        players[uid]={
        "xp":0,
        "level":1,
        "A":200,
        "streak":0,
        "last_day":"",
        "quests_done":[],
        "history":[]
        }

    return players[uid]

# ========================
# REALM SYSTEM
# ========================

def realm(level):

    if level<=100:
        stage=(level-1)//10+1
        return f"Luyện Khí tầng {stage}"

    realms=[
    "Trúc Cơ",
    "Kết Đan",
    "Nguyên Anh",
    "Hoá Thần",
    "Luyện Hư",
    "Hợp Thể",
    "Đại Thừa"
    ]

    index=(level-101)//100

    if index<len(realms):
        return realms[index]

    return "Tiên nhân"

# ========================
# LEVEL SYSTEM
# ========================

def xp_needed(p):

    level=p["level"]
    A=p["A"]

    B=1.5+(level//50)*0.1

    return int(A*(level**B))

def check_level(p):

    need=xp_needed(p)

    while p["xp"]>=need:

        p["xp"]-=need
        p["level"]+=1
        p["A"]+=10*p["level"]

        need=xp_needed(p)

# ========================
# RANDOM EVENT
# ========================

def random_event(p):

    e=random.choice(EVENTS)

    if "+150 XP" in e:
        p["xp"]+=150

    elif "+200 XP" in e:
        p["xp"]+=200

    elif "+1 streak" in e:
        p["streak"]+=1

    elif "A +5" in e:
        p["A"]+=5

    return e

# ========================
# AI GAME MASTER
# ========================

def ai_message(p):

    history="\n".join(p["history"][-5:])

    prompt=f"""
Ngươi là một hệ thống tu tiên cổ xưa.

Phong cách:
- văn phong tiên hiệp
- trang nghiêm
- đôi khi viết thơ cổ

Thông tin tu sĩ:

Cảnh giới: {realm(p["level"])}
Level: {p["level"]}
Streak: {p["streak"]}

Lịch sử tu luyện gần đây:
{history}

Hãy động viên tu luyện hôm nay.
"""

    r=client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role":"user","content":prompt}]
    )

    return r.choices[0].message.content

# ========================
# COMMANDS
# ========================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p=get_player(update.effective_user.id)

    text=f"""
【Hệ thống tu tiên khởi động】

Cảnh giới: {realm(p["level"])}
Level: {p["level"]}

Dùng /quests xem nhiệm vụ
"""

    await update.message.reply_text(text)

# ========================

async def quests(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p=get_player(update.effective_user.id)

    text="📜 Nhiệm vụ hôm nay\n\n"

    for i,q in enumerate(QUESTS):

        if i in p["quests_done"]:
            text+=f"✅ {i+1}. {q}\n"
        else:
            text+=f"{i+1}. {q}\n"

    await update.message.reply_text(text)

# ========================

async def done(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p=get_player(update.effective_user.id)

    if not context.args:
        await update.message.reply_text("/done số nhiệm vụ")
        return

    q=int(context.args[0])-1

    if q in p["quests_done"]:
        await update.message.reply_text("Đã hoàn thành rồi")
        return

    p["quests_done"].append(q)

    xp=100

    today=str(datetime.date.today())

    if p["last_day"]==today:
        p["streak"]+=1
    else:
        p["streak"]=1

    p["last_day"]=today

    bonus=p["streak"]*p["streak"]*p["level"]

    total=xp+bonus

    p["xp"]+=total

    p["A"]-=1

    log=f"{today} - Hoàn thành {QUESTS[q]}"
    p["history"].append(log)

    check_level(p)

    save_data()

    await update.message.reply_text(
    f"Hoàn thành {QUESTS[q]}\nXP +{total}"
    )

# ========================

async def stats(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p=get_player(update.effective_user.id)

    text=f"""
📊 Thông tin tu luyện

Cảnh giới: {realm(p["level"])}
Level: {p["level"]}
XP: {p["xp"]}
A: {p["A"]}
Streak: {p["streak"]}
"""

    await update.message.reply_text(text)

# ========================

async def history(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p=get_player(update.effective_user.id)

    if not p["history"]:
        await update.message.reply_text("Chưa có lịch sử")
        return

    text="📜 Nhật ký tu luyện\n\n"

    for h in p["history"][-10:]:
        text+=h+"\n"

    await update.message.reply_text(text)

# ========================
# DAILY RESET
# ========================

async def daily_reset(context:ContextTypes.DEFAULT_TYPE):

    for uid in players:

        p=players[uid]

        p["quests_done"]=[]

        event=random_event(p)

        try:

            msg=f"""
🌅 Thiên đạo dị tượng

{event}

Nhiệm vụ mới đã xuất hiện
"""

            ai=ai_message(p)

            await context.bot.send_message(
            chat_id=int(uid),
            text=msg+"\n"+ai
            )

        except:
            pass

    save_data()

# ========================
# MAIN
# ========================

def main():

    load_data()

    app=ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("quests",quests))
    app.add_handler(CommandHandler("done",done))
    app.add_handler(CommandHandler("stats",stats))
    app.add_handler(CommandHandler("history",history))

    app.job_queue.run_daily(
    daily_reset,
    time=datetime.time(hour=6,minute=0)
    )

    print("BOT STARTED")

    app.run_polling()

if __name__=="__main__":
    main()