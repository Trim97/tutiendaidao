from openai import OpenAI
from config import OPENAI_API_KEY
from memory import load_memory

client = OpenAI(api_key=OPENAI_API_KEY)

def chat(user_text):

    history = load_memory()

    history.append({
        "role":"user",
        "content":user_text
    })

    res = client.chat.completions.create(

        model="gpt-5-nano",

        messages=history

    )

    return res.choices[0].message.content