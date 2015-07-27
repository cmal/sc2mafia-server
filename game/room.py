#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- test-case-name: test.test_game -*-

#from game.game import Game
from game import Game
from player import Player

class Room(object):
    """
    game room
    """
    def __init__(self, name=u"", players=[], size=0):
        self.name = name
        self.players = players # []
        self.size = size
        self.game = Game(self) # create a game

    def change_size(self, size):
        """
        @type size: int
        """
        if size <= 20 and size >= len(self.game.players): # otherwise stay unchanged
            self.size = size

    def add_player(self, player):
        """
        @type player: C{Player}
        """
        if self.game.status == "ready":
            self.game.add_player(player)
        else:
            print "cannot add players after the game started."

    def remove_player(self, player):
        # 让错误显现
        self.players.remove(player)

    def is_full(self):
        if len(self.players) == self.size:
            return True
        else:
            return False
