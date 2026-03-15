from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Game Master đã thức tỉnh"}

@app.post("/webhook")
async def webhook(data: dict):

    message = str(data)

    if "chạy" in message:
        reply = "Thiếu hiệp đã hoàn thành thử luyện chạy. Tu vi +100."

    elif "đọc" in message:
        reply = "Luyện trí thành công. Tu vi tăng thêm."

    else:
        reply = "Thiên cơ khó dò. Bản tọa chưa hiểu ý ngươi."

    return JSONResponse(
        content={"reply": reply},
        media_type="application/json; charset=utf-8"
    )