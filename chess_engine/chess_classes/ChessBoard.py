
from django.template import loader

from chess_engine.chess_classes import ChessPiece
from chess_engine.chess_classes.simple_ai import core, parser
from chess_engine.models import GamePersistentData, UserColorSet
from utils import utils

import copy

AXIS = ['z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']


def offset(coordinate, delta):
    x = AXIS.index(coordinate) + delta
    if AXIS[x] in ['z', '0', '20']:
        return False
    return AXIS[x]


class Side:
    def __init__(self, name):
        self.name = name
        self.pieces = list()


class BoardColorSet:
    def __init__(self, user_id=None):
        colorset = dict()
        if user_id:
            user_colorset = UserColorSet.objects.filter(user=user_id).first()
            if not user_colorset:
                colorset = self.get_default_colorset()
            else:
                colorset = user_colorset.get_data('chess')
                if not colorset:
                    colorset = self.get_default_colorset()
        else:
            colorset = self.get_default_colorset()
        self.board_cell_light_color = colorset['board_cell_light_color']
        self.board_edge_cells_background_color = colorset['board_edge_cells_background_color']

    def get_default_colorset(self):
        res = dict()
        res['board_cell_light_color'] = 'e6bd73'
        res['board_edge_cells_background_color'] = 'ffffff'
        return res


class Board:
    template_name = 'chess_engine/board.html'

    def __init__(self, user_id):
        self.grid = dict()
        self.game_data = None
        self.sides = dict()
        self.sides['white'] = Side('white')
        self.sides['black'] = Side('black')
        self.kill_list = []

        self.color_set = BoardColorSet(user_id=user_id)

    def load_grid(self, game_data):
        self.game_data = game_data
        loaded_grid = self.game_data.get_data('board')
        if not loaded_grid:
            print('Board.load_grid: unfound data, so create new one.')
            self.load_new_grid()
            self.save_grid()
            print('Board.load_grid: created.')
        else:
            # build Pieces from data
            for line_key in loaded_grid:
                line = loaded_grid[line_key]
                for cell_key in line:
                    cell = line[cell_key]
                    if cell == '-':
                        utils.access(self.grid, '%s/%s' % (line_key, cell_key), '-')
                    else:
                        if cell['s'] == 'w':
                            side = self.sides['white']
                        else:
                            side = self.sides['black']

                        piece = ChessPiece.PiecePawn(self, cell['n'], side)
                        utils.access(self.grid, '%s/%s' % (line_key, cell_key), piece)

    def save_grid(self):
        self.game_data.set_data('board', self.grid)
        print('Board.save_grid: saved.')

    def load_new_grid(self):
        whites = Side('white')
        self.sides['white'] = whites

        blacks = Side('black')
        self.sides['black'] = blacks

        self.grid = {
            '19': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '18': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '17': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '16': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '15': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '14': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '13': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '12': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '11': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '10': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                   'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '9': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '8': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '7': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '6': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '5': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '4': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '3': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '2': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
            '1': {'a': '-', 'b': '-', 'c': '-', 'd': '-', 'e': '-', 'f': '-', 'g': '-', 'h': '-', 'i': '-',
                  'j': '-', 'k': '-', 'l': '-', 'm': '-', 'n': '-', 'o': '-', 'p': '-', 'q': '-', 'r': '-', 's': '-'},
        }

    def render(self, context):
        template = loader.get_template(self.template_name)
        context['board'] = self
        context['game'] = self.game_data
        context['game_data'] = self.game_data.get_data(None)
        context['material'] = self._measure_material()
        html_board = template.render(context)
        return html_board

    def is_cell_free(self, x, y):
        target_path = 'board/%s/%s' % (y, x)
        target_data = self.game_data.get_data(target_path)

        if target_data != '-':
            return False
        return True

    def is_dead(self, dead_list, current_side, x, y):
        # if the boundary cell is free
        # print("is_dead  x:%s, y:%s, dead_list: %s" % (x, y, dead_list))
        for i in [-1, 1]:
            x_ = offset(x, i)
            y_ = offset(y, i)

            if x_ is not False and [x_, y] not in dead_list:
                if self.grid[y][x_] == '-':
                    return False
            if y_ is not False and [x, y_] not in dead_list:
                if self.grid[y_][x] == '-':
                    return False

        # the boundary cell is not free
        # print("boundary cell not free")
        if offset(x, 1) is not False \
                and ([offset(x, 1), y] not in dead_list) and self.grid[y][offset(x, 1)].side.name == current_side:
            temp_list = self.is_dead(dead_list+[[offset(x, 1), y]], current_side, offset(x, 1), y)
            if not temp_list:
                return False
            else:
                dead_list += copy.deepcopy(temp_list)
        if offset(x, -1) is not False \
                and ([offset(x, -1), y] not in dead_list) and self.grid[y][offset(x, -1)].side.name == current_side:
            temp_list = self.is_dead(dead_list+[[offset(x, -1), y]], current_side, offset(x, -1), y)
            if not temp_list:
                return False
            else:
                dead_list += copy.deepcopy(temp_list)
        if offset(y, 1) is not False \
                and ([x, offset(y, 1)] not in dead_list) and self.grid[offset(y, 1)][x].side.name == current_side:
            temp_list = self.is_dead(dead_list+[[x, offset(y, 1)]], current_side, x, offset(y, 1))
            if not temp_list:
                return False
            else:
                dead_list += copy.deepcopy(temp_list)
        if offset(y, -1) is not False \
                and ([x, offset(y, -1)] not in dead_list) and self.grid[offset(y, -1)][x].side.name == current_side:
            temp_list = self.is_dead(dead_list+[[x, offset(y, -1)]], current_side, x, offset(y, -1))
            if not temp_list:
                return False
            else:
                dead_list += copy.deepcopy(temp_list)
        return dead_list

    def get_kill_list(self, x, y):
        self.kill_list = []
        # print("get_kill_list  x:%s, y:%s" % (x, y))

        current_side = self.game_data.get_data('token/step/side')
        enemy_side = 'black' if current_side == 'white' else 'white'

        for i in [-1, 1]:
            x_ = offset(x, i)
            y_ = offset(y, i)

            if x_ is not False \
                    and self.grid[y][x_] != '-' \
                    and self.grid[y][x_].side.name == enemy_side \
                    and [x_, y] not in self.kill_list:
                dead_list = self.is_dead([[x_, y]], enemy_side, x_, y)
                if dead_list is not False:
                    self.kill_list += copy.deepcopy(dead_list)
            if y_ is not False \
                    and self.grid[y_][x] != '-' \
                    and self.grid[y_][x].side.name == enemy_side \
                    and [x, y_] not in self.kill_list:
                dead_list = self.is_dead([[x, y_]], enemy_side, x, y_)
                if dead_list is not False:
                    self.kill_list += copy.deepcopy(dead_list)
        return self.kill_list

    def make_move(self, x, y):
        current_side = self.game_data.get_data('token/step/side')

        # 打劫
        if self.game_data.get_data('token/step/check') == 'T':
            if x == self.game_data.get_data('token/step/src_x') and y == self.game_data.get_data('token/step/src_y'):
                return False

        # try to make a move
        piece = ChessPiece.PiecePawn(self, 'p', self.sides[current_side])
        self.grid[y][x] = piece

        dead_list = self.get_kill_list(x, y)
        if len(dead_list) > 0 or self.is_dead([[x, y]], current_side, x, y) is False:
            self.sides[current_side].pieces.append(piece)
            self.game_data.set_data('board/{line}/{column}'.format(line=y, column=x), piece)
            self.kill()
            return True
        else:
            self.grid[y][x] = '-'
            return False

    def kill(self):
        # print("kill_list:", self.kill_list)

        # 存下吃子记录，用作判断打劫
        if len(self.kill_list) == 1:
            self.game_data.set_data('token/step/check', 'T')
            self.game_data.set_data('token/step/src_x', self.kill_list[0][0])
            self.game_data.set_data('token/step/src_y', self.kill_list[0][1])
        else:
            self.game_data.set_data('token/step/check', 'F')

        for x, y in self.kill_list:
            self.game_data.set_data('board/{line}/{column}'.format(line=y, column=x), '-')

    """ private """

    def _measure_material(self):
        """
        调用外部接口
        简单的形势判断
        """
        data = parser.parse_data(self.grid, 'white')
        solver = core.Solver(data)

        white, black = solver.measure()

        total = float(white + black)
        if total == 0:
            total += 1
        white_percent = round(white * 100 / total, 2)
        black_percent = 100 - white_percent

        result = {
            'brut': {'white': white, 'black': black},
            'percentages': {'white': white_percent, 'black': black_percent},
        }
        return result
