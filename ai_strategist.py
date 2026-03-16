from openai import OpenAI
from config import OPENAI_KEY

client=OpenAI(api_key=OPENAI_KEY)

def analyze_channel(data,history):

    prompt=f"""
You are a YouTube strategist.

Channel niche:
MrBeast style entertainment
Ryan Trahan storytelling
finance and crypto.

Channel growth:

{data}

Cultivation history:

{history}

Tasks:
1 analyze growth
2 suggest video idea
3 suggest title
4 suggest thumbnail
"""

    r=client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role":"user","content":prompt}]
    )

    return r.choices[0].message.content