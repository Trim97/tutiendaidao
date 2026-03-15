from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "BOT_TOKEN_CUA_BAN"

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    user_id = data["sender"]["id"]
    message = data["message"]["text"]

    if "chạy" in message.lower():
        reply = "Thiếu hiệp đã hoàn thành thử luyện chạy. Tu vi +100."
    else:
        reply = "Thiên cơ khó dò."

    url = "https://openapi.zalo.me/v2.0/oa/message"

    payload = {
        "recipient": {"user_id": user_id},
        "message": {"text": reply}
    }

    headers = {
        "access_token": BOT_TOKEN,
        "Content-Type": "application/json"
    }

    requests.post(url, json=payload, headers=headers)

    return {"status": "ok"}