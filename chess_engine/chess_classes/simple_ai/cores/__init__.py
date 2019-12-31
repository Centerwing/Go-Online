import imp

import chess_engine.chess_classes.simple_ai.cores.invalid_point
import chess_engine.chess_classes.simple_ai.cores.special_point
import chess_engine.chess_classes.simple_ai.cores.do_not_fill_itself
import chess_engine.chess_classes.simple_ai.cores.do_not_kill_friends
import chess_engine.chess_classes.simple_ai.cores.save_friends
import chess_engine.chess_classes.simple_ai.cores.connect_to_friends
import chess_engine.chess_classes.simple_ai.cores.connect_to_enemy
import chess_engine.chess_classes.simple_ai.cores.all_is_enemy
import chess_engine.chess_classes.simple_ai.cores.is_dangerous
import chess_engine.chess_classes.simple_ai.cores.attack
import chess_engine.chess_classes.simple_ai.cores.nearby
import chess_engine.chess_classes.simple_ai.cores.analyze
import chess_engine.chess_classes.simple_ai.cores.randomize

components = [
    invalid_point,
    special_point,
    do_not_fill_itself,
    do_not_kill_friends,
    save_friends,
    connect_to_friends,
    connect_to_enemy,
    all_is_enemy,
    is_dangerous,
    attack,
    nearby,
    analyze,
    randomize
]

judgers = []


def add_judger(func):
    global judgers

    judgers.append(func)


def judge(data, x, y):
    global judgers

    result = 0
    for judger in judgers:
        result += judger(data, x, y)

        # if (x, y) == (5, 2):
        #     print("(debug) {}".format(result))

        # if the score is too low
        if result < -9000000:
            break

    return result

for module in components:
    imp.reload(module)
    add_judger(module.judge)

