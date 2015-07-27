#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- test-case-name: test.test_game -*-

from player import Player

class Realm(object):
    """
    游戏国度，大区
    """
    def __init__(self, name=""):
        self.name = name
        self.rooms = {}
        self.players = {}

    def add_room(self,room):
        self.rooms[id(room)] = room

    def create_player(self):
        player = Player()
        self.players[id(player)]=player
        return player

    def count_players(self):
        return len(self.players)

    def count_in_room_players(self):
        return sum([len(room.players) for room in self.rooms.values()])

    def count_rooms(self):
        return len(self.rooms)

    def get_info(self):
        return u'该区当前有%d名玩家在线，%d个房间，有%d名玩家在房间中' % (
            self.count_players(),
            self.count_rooms(),
            self.count_in_room_players())
