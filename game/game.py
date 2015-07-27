#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- test-case-name: test.test_game -*-

import random

class GamePhase(object):
    """
    to record phases of a started game
    """
    def __init__(self,phase_id=0):
        self.phase_id = phase_id
        self.day = True
    def next():
        self.phase_id += 1

        
class Game(object):
    """
    客户端
    """
    def __init__(self, room=None):
        self.room = room
        self.players = self.room.players
        self.phase = GamePhase(0)
        self.size = self.room.size  # player size
        self.gossips = []
        self.roles = []
        self.seed = None # 随机数种子，游戏开始时从服务器获取，
                         # 服务器用random.choice(range(1,1000))
        self.status = "ready"  # alternatives: "ready", "started", "end"
        
    def add_player(self, player):
        self.players.append(player)
        
    def remove_player(self, player):
        self.players.remove(player)
        
    def get_dead_players(self):
        return [p for p in self.players if not p.alive]

    def get_groups(self):
        """
        the groups are
        'mafia','citizen','neutral', 'longtou?', and maybe 'random'
        @rtype: list
        """
        return set([g.group() for g in self.roles])
        

    def startGame(self):
        """
        这里应该做几项工作：
        1. 设置game.status
        2. 设置游戏phase
        3. （堵塞）从服务器获取 random seed，并设置random seed
        3. 用上述random seed，给每个player分配一个随机2~4单词的意大利人名
        4. 用上述random seed，给每个player分配一个随机座次（TODO:颜色）
        5. 初始化groups列表，用于判断游戏输赢（角色输赢不完全由此判断)
        6. ...
        """
        if self.status != "ready":
            # should raise GameNotReadyError
            pass
        self.status = "started"
        self.phase.next()
        names = [line.strip() for line in codecs.open('namelist','r','utf-8').readlines()]
        self.role_name = u' '.join(random.sample(names,random.choice(range(2,4))))
        random.seed(self.seed)
        random.shuffle(self.roles)
        random.shuffle(self.players) #这里是每个客户端独自获得的（相同）结果，不必再次通讯
        self.init_groups = getGroups()
        pass

    def remote_game_started(self, random_seed):
        self.seed = random_seed
        pass
