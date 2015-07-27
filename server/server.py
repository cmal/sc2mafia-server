#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.application import service
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.amp import AMP,Command
from twisted.internet.defer import Deferred
from twisted.python import log
import uuid
import sys

from game.realm import Realm
from game.room import Room
from client import Introduce, RealmInfo, JoinRoom, LeaveRoom


class GameServerProtocol(AMP):

    def __init__(self):
        pass
    
    def connectionMade(self):
#        log.msg(type(self.factory.chn_room.name))
#        log.msg("%s"%self.factory.chn_room.name)
        self.player = self.factory.realm.create_player()
        log.msg("player created, with identifier: %d" %(id(self.player),))
        log.msg(sys.getdefaultencoding())

    def connectionLost(self,reason):
        if self.player.room:
            self.leave_room()
        del self.factory.realm.players[id(self.player)]

    def set_player_name(self, player_name):
        log.msg(type(player_name))
        player_name = player_name.encode('utf-8')
        log.msg(player_name)
        self.player.name = player_name
        return {}
    Introduce.responder(set_player_name)

    def get_realm_info(self):
        amplist = []
        for room_id,room in self.factory.realm.rooms.items():
            room_dict = {'room_id': room_id,
                         'room_name': room.name,
                         'room_size': room.size}
            amplist.append(room_dict)
        return {'realm_name':self.factory.realm.name,
                'realm_info':self.factory.realm.get_info(),
                'rooms': amplist}
    RealmInfo.responder(get_realm_info)

    def join_room(self, room_id):
        """
        random_seed: String()
        player_dict: AmpBox({'player_id':'player_name',...})
        """
        log.msg("join room:%d"%room_id)
        self.player.room = self.factory.realm.rooms[room_id]
        self.player.room.add_player(self.player)
        amplist = []
        for p in self.player.room.players:
            player_dict = {'player_id': id(p),
                           'player_name': p.name.decode('utf-8')}
            amplist.append(player_dict)
        return {'random_seed':uuid.uuid4().hex,
                'players':amplist}
    JoinRoom.responder(join_room)

    def leave_room(self):
        # XXX if player in game, should notify other players
        log.msg("leave room:%d"%id(self.player.room))
        self.player.room.remove_player(self.player)
    LeaveRoom.responder(leave_room)


class GameServerFactory(Factory):

    protocol = GameServerProtocol

    def __init__(self, service):
        self.service = service
        self.realm = Realm(u"世界")
        self.chn_room = Room(u"中文房间",[],15)
        self.eng_room = Room(u"English Room",[],15)
        self.realm.add_room(self.chn_room)
        self.realm.add_room(self.eng_room)


class GameServerService(service.Service):

    def __init__(self):
        pass

    def startService(self):
        service.Service.startService(self)
