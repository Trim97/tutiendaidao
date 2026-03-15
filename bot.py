from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8642929480:AAH3oeIRu-NSYp5ulQdxf1NEUebZRIh5Z7E"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Game Master nhận: {text} (+100 XP)")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling()

if __name__ == "__main__":
    main()