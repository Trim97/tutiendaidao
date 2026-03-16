from database import cursor, conn

def save_memory(role,text):

    cursor.execute(
        "INSERT INTO memory(role,message) VALUES(?,?)",
        (role,text)
    )

    conn.commit()


def load_memory(limit=20):

    cursor.execute(
        "SELECT role,message FROM memory ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()

    history=[]

    for r in rows:

        history.append({
            "role":r[0],
            "content":r[1]
        })

    return list(reversed(history))