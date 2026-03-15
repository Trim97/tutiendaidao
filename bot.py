import json
import math
import datetime
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI


TOKEN = "8642929480:AAH3oeIRu-NSYp5ulQdxf1NEUebZRIh5Z7E"
import os

client = OpenAI(
    api_key=os.getenv("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")
)

DATA_FILE = "players.json"


QUESTS = [
"Chạy",
"Tập bụng",
"Dọn dẹp nhà cửa",
"Làm video youtube",
"Đọc sách ở thư viện",
"Làm game roblox",
"Ngủ đúng giờ",
"Review ngày cũ"
]


# =====================
# DATA
# =====================

def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {}

def save():
    with open(DATA_FILE,"w") as f:
        json.dump(players,f)

players = load()


def get_player(uid):

    uid = str(uid)

    if uid not in players:

        players[uid] = {
            "xp":0,
            "level":1,
            "A":200,
            "streak":0,
            "last_day":"",
            "quests_done":[]
        }

    return players[uid]


# =====================
# LEVEL
# =====================

def B(level):
    return 1.5 + math.floor(level/50)*0.1


def xp_need(p):
    return int(p["A"]*(p["level"]**B(p["level"])))


def level_up(p):

    while p["xp"] >= xp_need(p):

        p["xp"] -= xp_need(p)

        p["level"] += 1

        p["A"] += 10*p["level"]


# =====================
# REALM
# =====================

realms = [
"Trúc Cơ","Kết Đan","Nguyên Anh","Hoá Thần",
"Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp",
"Chân Tiên","Kim Tiên","Thái Ất Ngọc Tiên",
"Đại La","Đạo Tổ","Thiên Đạo","Thiên Đế","Đại Đế"
]


def realm(level):

    if level <= 100:
        return f"Luyện Khí tầng {(level-1)//10+1}"

    level -= 100
    r = level//100

    phase = level%100

    if phase < 30:
        p = "Sơ Kỳ"
    elif phase < 60:
        p = "Trung Kỳ"
    elif phase < 90:
        p = "Hậu Kỳ"
    else:
        p = "Đỉnh Phong"

    return f"{realms[r]} {p}"


# =====================
# AI GAME MASTER
# =====================

def ai_message(player):

    prompt = f"""
Ngươi là một HỆ THỐNG TU TIÊN cổ xưa.

Phong cách nói chuyện:
- Văn phong tiên hiệp Trung Hoa
- Trang nghiêm
- Có thể trích thơ cổ hoặc tự sáng tác thơ
- Giống hệ thống trong truyện tu tiên

Thông tin tu sĩ:

Cảnh giới: {realm(player["level"])}
Level: {player["level"]}
Streak tu luyện: {player["streak"]}

Hãy:

1. Giao nhiệm vụ hôm nay
2. Động viên tu luyện
3. Thỉnh thoảng viết 1-2 câu thơ cổ phong

Nhiệm vụ hôm nay:

1. Chạy
2. Tập bụng
3. Dọn dẹp nhà cửa
4. Làm video youtube
5. Đọc sách ở thư viện
6. Làm game roblox
7. Ngủ đúng giờ
8. Review ngày

Hãy viết như một thông báo từ HỆ THỐNG TU TIÊN.
"""

    r = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role":"user","content":prompt}]
    )

    return r.choices[0].message.content


# =====================
# COMMANDS
# =====================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p = get_player(update.effective_user.id)

    msg = ai_message(p)

    await update.message.reply_text(msg)


async def profile(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p = get_player(update.effective_user.id)

    text = f"""
Cảnh giới: {realm(p["level"])}
Level: {p["level"]}
XP: {p["xp"]}/{xp_need(p)}

Streak: {p["streak"]}
Hệ số A: {p["A"]}
"""

    await update.message.reply_text(text)


async def quest(update:Update,context:ContextTypes.DEFAULT_TYPE):

    text="Nhiệm vụ hôm nay:\n\n"

    for i,q in enumerate(QUESTS):
        text+=f"{i+1}. {q}\n"

    text+="\nHoàn thành: /done số"

    await update.message.reply_text(text)


async def done(update:Update,context:ContextTypes.DEFAULT_TYPE):

    p = get_player(update.effective_user.id)

    q = int(context.args[0])-1

    if q in p["quests_done"]:
        await update.message.reply_text("Quest đã hoàn thành.")
        return

    today = str(datetime.date.today())

    if p["last_day"]!=today:

        if p["last_day"] == str(datetime.date.today()-datetime.timedelta(days=1)):
            p["streak"]+=1
        else:
            p["streak"]=1

        p["last_day"]=today
        p["quests_done"]=[]

    p["quests_done"].append(q)

    bonus = p["streak"]*p["streak"]*p["level"]

    gain = 100 + bonus

    p["xp"]+=gain

    p["A"]-=1

    level_up(p)

    save()

    await update.message.reply_text(f"+{gain} XP")


# =====================
# DAILY RESET
# =====================

async def daily_reset(app):

    for uid in players:

        players[uid]["quests_done"]=[]

    save()

    for uid in players:

        p = players[uid]

        msg = ai_message(p)

        await app.bot.send_message(uid,msg)


# =====================
# MAIN
# =====================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("profile",profile))
    app.add_handler(CommandHandler("quest",quest))
    app.add_handler(CommandHandler("done",done))

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        daily_reset,
        "cron",
        hour=6,
        args=[app]
    )

    scheduler.start()

    app.run_polling()


if __name__=="__main__":
    main()