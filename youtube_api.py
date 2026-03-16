import requests
from config import YOUTUBE_API_KEY,CHANNEL_ID

def get_channel_stats():

    url=f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"

    r=requests.get(url).json()

    stats=r["items"][0]["statistics"]

    return {
        "subs":int(stats["subscriberCount"]),
        "views":int(stats["viewCount"])
    }