#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- test-case-name: test.test_game -*-

from role import Role

class User(object): # TODO: authenticate

    def __init__(self,auth_id=0,name=u""):
        self.auth_id = auth_id
        self.authenticated = False
        if name == u"":
            self.name = "Guest_%s"%(id,)
        else:
            self.name = name

class Player(object):

    def __init__(self,room=None,name=u""):
        self.room = room
        self.name = name # 长度20unicode
        # self.user_name = self.user.name
                
    def join_room(self,room=None):  # 都应该有服务器消息
        if room != None:
            self.room = room
            print "join room %d" % (room.id,)
    def leave_room(self):
        self.room = None
        print "leave room %d" % (room.id,)
