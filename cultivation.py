from database import cursor, conn

def get_player():

    cursor.execute("SELECT * FROM player WHERE id=1")

    p = cursor.fetchone()

    if not p:

        cursor.execute("""
        INSERT INTO player VALUES(1,'Đạo Hữu',1,0,0,200,1.5)
        """)

        conn.commit()

        return get_player()

    return p


def add_xp(amount):

    p = get_player()

    level = p[2]
    xp = p[3] + amount
    A = p[5]
    B = p[6]

    need = int(A * (level ** B))

    if xp >= need:

        level += 1
        xp = 0

        A += 10 * level

        if level % 50 == 0:
            B += 0.1

    cursor.execute(
        "UPDATE player SET level=?,xp=?,A=?,B=? WHERE id=1",
        (level, xp, A, B)
    )

    conn.commit()