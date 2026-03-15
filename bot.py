from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "BOT_TOKEN_CUA_BAN"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    reply = f"Game Master nhận: {text} (+100 XP)"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()