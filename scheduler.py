from youtube_api import get_channel_stats
from youtube_analyzer import analyze_growth
from ai_strategist import analyze_channel
from memory_engine import save_cultivation,get_history

async def daily_report(context):

    bot=context.bot

    today=get_channel_stats()

    yesterday=context.bot_data.get("yt_yesterday")

    if yesterday is None:
        context.bot_data["yt_yesterday"]=today
        return

    growth=analyze_growth(today,yesterday)

    history=await get_history(30)

    analysis=analyze_channel(growth,history)

    msg=f"""
🌙 Thiên cơ báo cáo

Subscriber +{growth['sub_gain']}
Views +{growth['view_gain']}

📊 Phân tích chiến lược

{analysis}
"""

    await bot.send_message(context.bot_data["owner"],msg)

    context.bot_data["yt_yesterday"]=today

