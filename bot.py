from telegram.ext import ApplicationBuilder,MessageHandler,filters
from config import TELEGRAM_TOKEN
from database import init_db

async def chat(update,context):

    text=update.message.text.lower()

    if "chạy" in text:

        await update.message.reply_text("✔ Nhiệm vụ chạy hoàn thành")

    elif "video" in text:

        await update.message.reply_text("📹 Nhiệm vụ youtube hoàn thành")

    else:

        await update.message.reply_text("Hệ thống đã ghi nhận lời nói của tu sĩ.")

async def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(MessageHandler(filters.TEXT, chat))

    print("BOT RUNNING")

    await app.run_polling()