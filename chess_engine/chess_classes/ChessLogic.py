
from chess_engine.chess_classes import ChessBoard, ChessPiece
from chess_engine.chess_classes.simple_ai import core, parser
from chess_engine.chess_classes.ChessExercises import get_exercise_board
from utils import utils
from chess_engine.models import *


class ChessGame:
    def __init__(self, user_id, game_id=None):
        self.board = ChessBoard.Board(user_id=user_id)

        if game_id:
            self.game_id = game_id
            self.load_game(game_id)
        else:
            self.game_data = self.initialize()

    def initialize(self, give_hand_to='black'):
        # create GamePersistentData
        # create Board
        # store board in game
        # give token to white side
        self.game_data = GamePersistentData.objects.filter(id=self.game_id).first()
        if not self.game_data:
            self.game_data = GamePersistentData()
            self.game_id = self.game_data.id

        self._initialize_castle_data()
        self.game_data.set_data('token/step/name', 'waitCellSource')
        self.game_data.set_data('token/step/side', give_hand_to)
        self.game_data.set_data('token/step/last_pass', 'no')
        self.game_data.set_data('token/step/data/impossible_move', '-')

        if self.game_data.get_data('game_options/exercise'):
            self.load_exercise_board()

        return self.game_data

    def load_game(self, game_id):
        # load GamePersistentData context :
        # - position of pieces on board
        # - game state (token)
        # give token to player
        self.game_id = game_id
        self.game_data = GamePersistentData.objects.filter(id=self.game_id).first()
        self.board.load_grid(self.game_data)
        return True

    """ user actions """

    """ game management """
    def create_game(self):
        pass

    def delete_game(self):
        pass

    """ starting game """
    def join_game(self, user):
        pass

    def select_colorset(self, user, colorset):
        pass

    def select_side(self, user, side):
        pass

    """ during game """
    def make_a_pass(self):
        self.game_data.set_data('token/step/data/impossible_move', '-')

        last_pass = self.game_data.get_data('token/step/last_pass')

        if last_pass == 'yes':
            data = parser.parse_data(self.board.grid, 'white')
            solver = core.Solver(data)

            white, black = solver.measure()
            if white+7.5 > black:
                self.game_data.set_data('token/step/side', 'black')
            else:
                self.game_data.set_data('token/step/side', 'white')
            self.accept_checkmate()
            return True

        self.game_data.set_data('token/step/last_pass', 'yes')

        side = self.game_data.get_data('token/step/side')
        move_data = {
            'current_side': side,
            'dest_x': 'None',
            'dest_y': '',
        }

        # finishing moving
        self._finalize_turn(move_data)

        # ai move
        if self.game_data.get_data('game_options/ai'):
            self._ai_move(move_data)

        return True

    def move_piece_select_target(self, user, x, y):
        self.game_data.set_data('token/step/data/impossible_move', '-')

        # verify if cell is free
        if not self.board.is_cell_free(x, y):
            print('ChessGame.move_piece_select_target: cell is not free.')
            self.game_data.set_data('token/step/data/impossible_move', 'cell is not free')
            return False

        # verify if move is valid
        if not self.board.make_move(x, y):
            print('ChessGame.move_piece_select_target: move is invalid.')
            self.game_data.set_data('token/step/data/impossible_move', 'no liberty')
            return False

        # set pass flag -> no
        self.game_data.set_data('token/step/last_pass', 'no')

        side = self.game_data.get_data('token/step/side')
        move_data = {
            'current_side': side,
            'dest_x': x,
            'dest_y': y,
        }

        # finishing moving
        self._finalize_turn(move_data)

        # ai move
        if self.game_data.get_data('game_options/ai'):
            self._ai_move(move_data)

        return True

    """ end of game """
    # - accept checkmate
    # - accept revanche
    # - accept belle
    # - quit game (-> sauver)

    def reset_round(self):
        history = self.game_data.get_data('history')
        game_options = self.game_data.get_data('game_options')
        participants = self.game_data.get_data('participants')
        rounds = self.game_data.get_data('rounds')
        self.game_data.set_data(None, {})
        self.game_data.set_data('history', history)
        self.game_data.set_data('game_options', game_options)
        self.game_data.set_data('participants', participants)
        self.game_data.set_data('rounds', rounds)
        self.initialize()

    def reset_game(self):
        game_options = self.game_data.get_data('game_options')
        participants = self.game_data.get_data('participants')
        self.game_data.set_data(None, {})
        self.game_data.set_data('game_options', game_options)
        self.game_data.set_data('participants', participants)
        self.initialize()

    def accept_checkmate(self):
        print('ChessLogic.accept_checkmate')
        self.game_data.set_data('token/step/name', 'checkmate')
        self.game_data.set_data('token/result', 'checkmate')
        self._save_game('checkmate')

        if self._winning_games_gap_reached():
            # nothing to do
            pass
        else:
            # prepare next hand
            current_round_number = 1
            rounds = self.game_data.get_data('rounds')
            if rounds:
                current_round_number += len(rounds)
            if current_round_number % 2 == 0:
                next_side = 'white'
            else:
                next_side = 'black'
            print('give hand to next side : %s' % next_side)
            self.initialize(give_hand_to=next_side)

    def declare_withdraw(self):
        print('ChessLogic.declare_withdraw')
        self.game_data.set_data('token/step/name', 'withdraw')
        self.game_data.set_data('token/result', 'checkmate')

        self._save_game('withdraw')
        if self._winning_games_gap_reached():
            print('_winning_games_gap_reached')
            pass
        else:
            next_side = 'black' if self.game_data.get_data('token/step/side') == 'white' else 'white'
            self.initialize(give_hand_to=next_side)

    def declare_draw(self):
        print('ChessLogic.declare_draw')
        # todo

    def accept_revanche(self, user):
        pass

    def accept_belle(self, user):
        pass

    def quit_game(self, user):
        pass

    """ private mechanics tools """

    def _initialize_castle_data(self):
        rookable_data = ['r1', 'r2']
        self.game_data.set_data('token/step/castle/white', rookable_data)
        self.game_data.set_data('token/step/castle/black', rookable_data)

    def _winning_games_gap_reached(self):
        # check if number of required winning games is reached
        winning_games = int(self.game_data.get_data('game_options/winning_games'))
        rounds = self.game_data.get_data('rounds')
        number_of_white_wins = 0
        number_of_black_wins = 0
        for round_k, round in rounds.items():
            if round['winner'] == 'white':
                number_of_white_wins += 1
            elif round['winner'] == 'black':
                number_of_black_wins += 1

        if (number_of_white_wins >= winning_games) or (number_of_black_wins >= winning_games):
            return True
        return False

    def _save_game_result(self, result):
        side = self.game_data.get_data('token/step/side')
        if side == 'white':
            winner_side = 'black'
        else:
            winner_side = 'white'
        rounds = self.game_data.get_data('rounds')
        round_result = dict()
        round_result['result'] = result
        round_result['winner'] = winner_side
        if rounds:
            new_round_path = 'rounds/%d' % (len(rounds) + 1)
        else:
            new_round_path = 'rounds/1'
        self.game_data.set_data(new_round_path, round_result)

        if self._winning_games_gap_reached():
            print ('_winning_games_gap_reached')
            self.game_data.set_data('result/winner', winner_side)
            round_list = ''
            rounds = self.game_data.get_data('rounds')
            round_count = 1
            while round_count <= len(rounds):
                round_path = 'rounds/%d/winner' % round_count
                round_winner = self.game_data.get_data(round_path)
                if round_winner == 'white':
                    round_list += 'w'
                elif round_winner == 'black':
                    round_list += 'b'
                else:
                    print ('warning : unknown side : %s' % round_winner)
                round_count += 1
            self.game_data.set_data('result/round_list', round_list)

            # update elo if ranked game
            ranked_game = self.game_data.get_data('game_options/ranked')
            if ranked_game:
                if winner_side == 'white':
                    winner_user = User.objects.filter(id=self.game_data.get_data('participants/white/1')).first()
                    loser_user = User.objects.filter(id=self.game_data.get_data('participants/black/1')).first()
                else:
                    winner_user = User.objects.filter(id=self.game_data.get_data('participants/black/1')).first()
                    loser_user = User.objects.filter(id=self.game_data.get_data('participants/white/1')).first()
                winner_ranking = UserRanking.objects.get_or_create(user=winner_user)[0]
                loser_ranking = UserRanking.objects.get_or_create(user=loser_user)[0]
                winner_old_elo = int(winner_ranking.get_elo('chess'))
                if not winner_old_elo:
                    winner_old_elo = 0
                loser_old_elo = int(loser_ranking.get_elo('chess'))
                if not loser_old_elo:
                    loser_old_elo = 0
                d = loser_old_elo - winner_old_elo
                loser_ranking.update_elo('chess', w=0, d=d, game_id=self.game_data.id,
                                         opponent_id=winner_user.id, opponent_elo=winner_old_elo)
                winner_ranking.update_elo('chess', w=1, d=d, game_id=self.game_data.id,
                                          opponent_id=loser_user.id, opponent_elo=loser_old_elo)
                print('ChessGame._save_game_results: elo updated : loser:%s, winner:%s'
                      % (loser_ranking.get_elo('chess'), winner_ranking.get_elo('chess')))

    def _save_game(self, result):
        # backup data
        history = self.game_data.get_data('history')
        game_options = self.game_data.get_data('game_options')
        participants = self.game_data.get_data('participants')
        saved_games = self.game_data.get_data('saved_games')

        # save round results
        self._save_game_result(result)
        rounds = self.game_data.get_data('rounds')
        results = self.game_data.get_data('result')

        # add round to history
        history_game = dict()
        history_game['token'] = self.game_data.get_data('token')
        history_game['board'] = self.game_data.get_data('board')
        if history:
            new_game_key = 'game_%02d' % (len(history) + 1)
        else:
            history = dict()
            new_game_key = 'game_01'
        history[new_game_key] = history_game

        # prepare game data for a new round
        self.game_data.set_data(None, {})
        self.game_data.set_data('history', history)
        self.game_data.set_data('game_options', game_options)
        self.game_data.set_data('participants', participants)
        self.game_data.set_data('rounds', rounds)
        self.game_data.set_data('result', results)
        self.game_data.set_data('saved_games', saved_games)

    def _finalize_turn(self, move_data):
        side = self.game_data.get_data('token/step/side')

        # reload grid
        self.board.load_grid(self.game_data)

        self.game_data.set_data('token/step/name', 'waitCellSource')

        if side == 'white':
            self.game_data.set_data('token/step/side', 'black')
        else:
            self.game_data.set_data('token/step/side', 'white')

        self.game_data.add_log(move_data)

    def load_exercise_board(self):
        grids = get_exercise_board(self.board)

        index = 1
        for grid in grids:
            saved_game = {
                'comment': 'Exercises '+str(index),
                'board': grid,
                'token': self.game_data.get_data('token')
            }
            saved_index = '%03d.' % index
            self.game_data.set_data('saved_games/%s' % saved_index, saved_game)
            index += 1

    def _ai_move(self, move_data):
        """
        调用外部接口
        简单的AI决策
        """
        data = parser.parse_data(self.board.grid, self.game_data.get_data('token/step/side'), move_data)
        solver = core.Solver(data)
        x, y = solver.compute()

        if not self.board.make_move(x, y):
            print('! ai wrong !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            return False

        # set pass flag -> no
        self.game_data.set_data('token/step/last_pass', 'no')

        side = self.game_data.get_data('token/step/side')
        move_data = {
            'current_side': side,
            'dest_x': x,
            'dest_y': y,
        }

        # finishing moving
        self._finalize_turn(move_data)
