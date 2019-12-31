from chess_engine.chess_classes.simple_ai.cores.defs import *

import random

RANDOMIZE_MIN = -200
RANDOMIZE_MAX = 200

def judge(data, x, y):
    return random.randint(RANDOMIZE_MIN, RANDOMIZE_MAX)
