def analyze_growth(today,yesterday):

    sub_gain=today["subs"]-yesterday["subs"]
    view_gain=today["views"]-yesterday["views"]

    score=sub_gain*5 + view_gain*0.1

    return {
        "sub_gain":sub_gain,
        "view_gain":view_gain,
        "score":score
    }