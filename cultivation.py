import math

def xp_needed(player):

    level=player["level"]
    A=player["A"]

    B=1.5+(level//50)*0.1

    return int(A*(level**B))
def level_up(player):

    need=xp_needed(player)

    while player["xp"]>=need:

        player["xp"]-=need
        player["level"]+=1
        player["A"]+=10*player["level"]

        need=xp_needed(player)