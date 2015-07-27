#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- test-case-name: test.test_game -*-

class Role(object):
    def __init__(self,name="",group=None):
        """
        游戏中的角色，名称、任务等均可变化
        @type group: tuple, should be (u'namePinyin',u'nameChn')
        """
        # 玩家信息
        self.alive = True
        self.lw = " \n " # last words 遗言。取用时用split("\n")分割
        # 角色信息
        self.name = name
        self.group = group # tuple，城镇、黑手党等
        self.ability = None
        self.chartype = None  # 调查，保护等
        self.mission = None  # 其他以后添加
