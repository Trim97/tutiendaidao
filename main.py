from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "BOT_TOKEN_CUA_BAN"

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("ZALO DATA:", data)

    if data.get("event_name") == "message.text.received":

        user_id = data["message"]["from"]["id"]
        text = data["message"]["text"]

        reply = f"Game Master đã nhận: {text} (+100 XP)"

        url = "https://openapi.zalo.me/v2.0/oa/message"

        payload = {
            "recipient": {"user_id": user_id},
            "message": {"text": reply}
        }

        headers = {
            "access_token": "2593478870267479601:sBlndTwWqpZNMUEFxJoNJdoUevWTSbZVKYXpoHHEmYRKHmVOMdRrUCHywdWUgWHt",
            "Content-Type": "application/json"
        }

        requests.post(url, json=payload, headers=headers)

    return {"status": "ok"}