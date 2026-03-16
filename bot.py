from telegram.ext import ApplicationBuilder,MessageHandler,filters

from config import TELEGRAM_TOKEN

from database import init_db,cursor,conn

from ai_chat import chat
from memory import save_memory

from scheduler import nightly_report

async def handle(update,context):

    text=update.message.text

    chat_id=update.message.chat.id

    cursor.execute(
        "INSERT OR REPLACE INTO settings VALUES('chat_id',?)",
        (chat_id,)
    )

    conn.commit()

    save_memory("user",text)

    reply=chat(text)

    save_memory("assistant",reply)

    await update.message.reply_text(reply)


def main():

    init_db()

    app=ApplicationBuilder().token(
        TELEGRAM_TOKEN
    ).build()

    app.add_handler(
        MessageHandler(filters.TEXT,handle)
    )

    job_queue=app.job_queue

    job_queue.run_daily(
        nightly_report,
        time={"hour":21,"minute":0}
    )

    print("BOT RUNNING")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__=="__main__":

    main()