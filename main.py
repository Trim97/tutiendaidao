from fastapi import FastAPI, Request
import requests

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("ZALO DATA:", data)

    return {"status": "ok"}