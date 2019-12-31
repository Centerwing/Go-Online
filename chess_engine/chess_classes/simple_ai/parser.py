from chess_engine.chess_classes.simple_ai import core

from chess_engine.chess_classes.simple_ai.config import *


def parse_data(data, side, move_data=None):
    result = core.BoardData()

    for line_k, line in data.items():
        for cell_k, cell in line.items():
            if cell == '-':
                result.set(core.X_INDEX.index(line_k), core.Y_INDEX.index(cell_k), 0)
            elif cell.side.name == 'white':
                result.set(core.X_INDEX.index(line_k), core.Y_INDEX.index(cell_k), 1)
            else:
                result.set(core.X_INDEX.index(line_k), core.Y_INDEX.index(cell_k), 2)

    if side == 'white':
        result.current = 1
    else:
        result.current = 2

    if move_data is not None:
        if move_data['dest_x'] != 'None':
            x = core.X_INDEX.index(move_data['dest_y'])
            y = core.Y_INDEX.index(move_data['dest_x'])
            result.history.append([x, y])
        else:
            result.history.append([10, 10])

    return result
