from fastapi import FastAPI, Request
import requests

app = FastAPI()

BOT_TOKEN = "2593478870267479601:sBlndTwWqpZNMUEFxJoNJdoUevWTSbZVKYXpoHHEmYRKHmVOMdRrUCHywdWUgWHt"

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("ZALO DATA:", data)

    if data.get("event_name") == "message.text.received":

        user_id = data["message"]["from"]["id"]
        text = data["message"]["text"]

        reply = f"Game Master đã nhận: {text} (+100 XP)"

        url = "https://bot-api.zapps.me/v1/message/send"

        payload = {
            "recipient": {
                "user_id": user_id
            },
            "message": {
                "text": reply
            }
        }

        headers = {
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type": "application/json"
        }

        r = requests.post(url, json=payload, headers=headers)

        print("ZALO SEND RESULT:", r.text)

    return {"status": "ok"}