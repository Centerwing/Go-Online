from abc import ABCMeta, abstractmethod


class PieceRole:
    def __init__(self, name, label, weight):
        self.name = name
        self.label = label
        self.weight = weight


class Piece(object):
    __metaclass__ = ABCMeta

    def __init__(self, board, name, picture, side):
        self.name = name
        self.side = side
        self.picture = picture

        self.board = board

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __json__(self):
        return {'n': self.name, 's': self.side.name[0:1]}

    """ abstract public """

    """ abstract private """

    """ public """

    """ private """


class PiecePawn(Piece):
    def __init__(self, board, name, side):
        Piece.__init__(self, board, name, 'pawn.png', side)

    """ abstract implementations """

    """ private specific implementations """
