import requests

from config import YOUTUBE_API_KEY, CHANNEL_ID
from database import cursor, conn
from cultivation import add_xp

def scan():

    try:

        url="https://www.googleapis.com/youtube/v3/channels"

        params={
            "part":"statistics",
            "id":CHANNEL_ID,
            "key":YOUTUBE_API_KEY
        }

        r=requests.get(url,params=params)

        data=r.json()

        stats=data["items"][0]["statistics"]

        subs=int(stats["subscriberCount"])
        views=int(stats["viewCount"])

    except:

        return 0,None

    cursor.execute("SELECT subs,views FROM youtube_stats LIMIT 1")

    row=cursor.fetchone()

    if not row:

        cursor.execute(
            "INSERT INTO youtube_stats VALUES(?,?)",
            (subs,views)
        )

        conn.commit()

        return 0,None

    old_subs,old_views=row

    delta_sub=subs-old_subs
    delta_view=views-old_views

    xp=(delta_sub+delta_view)*10

    if xp>0:
        add_xp(xp)

    cursor.execute(
        "UPDATE youtube_stats SET subs=?,views=?",
        (subs,views)
    )

    conn.commit()

    event=None

    if delta_view>=1000000:
        event="🌟 Đại Cơ Duyên"

    elif delta_view>=100000:
        event="✨ Trung Cơ Duyên"

    elif delta_view>=10000:
        event="🔹 Tiểu Cơ Duyên"

    return xp,event