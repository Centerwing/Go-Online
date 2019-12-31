from django import forms
from django.core.validators import RegexValidator
from .models import GamePersistentData
from chess_engine.chess_classes import ChessLogic


class CreateChessGameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(CreateChessGameForm, self).__init__(*args, **kwargs)
        self.fields['winning_games'].choices = [('1', '1'), ('2', '2'), ('3', '3')]
        self.fields['play_as'].choices = [('white', 'White'), ('black', 'Black'),
                                          ('vs_ai', 'Vs AI'), ('do_not_play', 'Do not play')]

    name = forms.CharField(label='Game name', max_length=200,
                           validators=[RegexValidator(regex='^[a-zA-Z0-9_-]*$', message='Invalid Game Name')])
    winning_games = forms.ChoiceField(label='Winning games', choices=())
    play_as = forms.ChoiceField(label='Play as', choices=())
    public = forms.BooleanField(label='Public game', required=False)
    ranked = forms.BooleanField(label='Ranked game', required=False)

    def execute(self):
        try:
            name = self.cleaned_data['name']
            winning_games = self.cleaned_data['winning_games']
            play_as = self.cleaned_data['play_as']
            public = self.cleaned_data['public']
            ranked = self.cleaned_data['ranked']

            game = GamePersistentData()

            game.set_data('game_options/name', name)
            game.set_data('game_options/winning_games', winning_games)
            game.set_data('game_options/public', public)
            game.set_data('game_options/ranked', ranked)
            game.set_data('game_options/creator', self.request.user.id)
            if play_as == 'white' or play_as == 'black':
                game.set_data('participants/%s/1' % play_as, self.request.user.id)
            if play_as == 'vs_ai':
                game.set_data('participants/black/1', self.request.user.id)
                game.set_data('participants/white/1', '100')
                game.set_data('game_option/ai', 'True')
            else:
                game.set_data('game_option/ai', 'False')

            game.save()

            game_logic = ChessLogic.ChessGame(user_id=self.request.user.id, game_id=game.id)
            game_logic.initialize(give_hand_to='black')

        except Exception as e:
            return False, 'Game creation error : %s' % e.message
        return True, game
