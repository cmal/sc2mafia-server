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
from network import Introduce, AuthPlayer, RealmInfo, JoinRoom, LeaveRoom
from auth.auth import make_password, check_password
from db import User, SessionMaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError


class GameServerProtocol(AMP):

    def __init__(self):
        self.session = SessionMaker()

    def connectionMade(self):
        self.player = self.factory.realm.create_player()
        log.msg("player created, with identifier: %d" %(id(self.player),))
        log.msg(sys.getdefaultencoding())

    def connectionLost(self,reason):
        if self.player.room:
            self.leave_room()
        del self.factory.realm.players[id(self.player)]

    def auth_create_player(self, session, name, password): 
        """ name:unicode, password:unicode
        """
        q = session.query(User).filter_by(name=name).all()
        if q: #auth player
            b = self.auth_player(name, password)
            if b:
                return 'player authed'
            else:
                return 'auth failed'
        else: #create player
            try:
                u = User(name, password)
                session.add(u)
                session.commit()
#            except IntegrityError:
#                return 'player_name already exists'
            except InvalidRequestError:
                raise session.rollback()
                return 'null player_name or null password'
            return 'player created'


    def introduce(self, player_name, password):
        log.msg(player_name, password)
        self.player.name = player_name
        encoded_pswd = make_password(password)
        return {'message': self.auth_create_player(self.session,
                                              player_name,
                                              encoded_pswd)}
    Introduce.responder(introduce)

    def auth_player(self, name, password):
        log.msg(name, password) #unicode, unicode
        pswd = self.session.query(User.password).\
                        filter_by(name=name).scalar()
        log.msg("type of pswd(query result):", type(pswd))
        if check_password(password, pswd):
            return True
        else:
            return False
#    AuthPlayer.responder(auth_player)

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
