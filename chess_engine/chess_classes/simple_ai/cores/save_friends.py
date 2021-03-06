from chess_engine.chess_classes.simple_ai.cores.defs import *

UNIT_SCORE = 70000
CHESS_SCORE = 35000
DANGEROUS_SCORE = 60000
DANGEROUS_LIMIT = 1

def judge(data, x, y):
    score = 0
    neighbor = [
        (-1, 0), (1, 0),
        (0, -1), (0, 1)
    ]

    for dx, dy in neighbor:
        cx = x + dx
        cy = y + dy
        if data.is_in_range(cx, cy) and data.get(cx, cy) == data.current:
            doors = data.get_weak_doors(cx, cy)

            if len(doors) <= DANGEROUS_LIMIT and (x, y) in doors:
                # print("(debug) {}, {} is dangerous".format(cx, cy))
                saved = len(data.get_connected_component(cx, cy))
                data.set(x, y, data.current)
                now = len(data.get_weak_doors(x, y))
                score += ((now - len(doors)) * UNIT_SCORE +
                    saved * CHESS_SCORE +
                    (DANGEROUS_LIMIT - len(doors)) * DANGEROUS_SCORE)
                data.set(x, y, EMPTY)

    return score
