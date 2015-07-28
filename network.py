#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import Deferred
from twisted.protocols.amp import AMP, Command, Integer, String, Unicode, AmpList
from game.realm import Realm
from game.room import Room
import random

class RealmInfo(Command):
    response = [('realm_name', Unicode()),
                ('realm_info', Unicode()),
                ('rooms', AmpList([('room_id', Integer()),
                                   ('room_name', Unicode()),
                                   ('room_size', Integer())]))]

class Introduce(Command):
    arguments = [('player_name', Unicode()),
                 ('password', Unicode())]
    response = []

class JoinRoom(Command):
    arguments = [('room_id', Integer())]
    response = [('random_seed', String()),
                ('players', AmpList([('player_id', Integer()),
                                     ('player_name', Unicode())]))]

class LeaveRoom(Command):
    pass

def global_no_err_back(err):
    print "global_no_err_back:Error\n"
    print err
def global_no_call_back(*args):
    print "global_no_call_back:\n"
    for i in args:
        print i

class GameClientProtocol(AMP):

    def connectionMade(self):
        self.callRemote(Introduce,player_name=self.player_name).addCallback(global_no_call_back).addErrback(global_no_err_back)
        self.callRemote(RealmInfo).addCallback(self.got_realm_info).addErrback(global_no_err_back)


    def connectionLost(self, reason):
        print "connection lost %s" % reason
        pass

    def introduce(self): # XXX identifier没用 删掉
        return self.callRemote(Introduce).addErrback(global_no_err_back)

#    def player_introduced(self,result):
#        print "got player id from server:%d"%(result['identifier'],)
#        self.player_id = result['identifier']
    def player_introduced(self):
        pass

    def join_room(self, room_id):
        self.room_id_for_join = room_id
        self.room_id = 0
        return self.callRemote(JoinRoom,room_id=room_id).addCallback(self.joined_room).addErrback(global_no_err_back)

    def joined_room(self, result):
        self.room_id = self.room_id_for_join
        random_seed = result['random_seed']
        players = result['players']
        room_info = ""
        for p in players:
            room_info += "player_id:%s, player_name:%s"%(p['player_id'],p['player_name'])
        print "You have joined room %d.This room has %d players,and the random_seed is %s.rooms info:%s"\
            %(self.room_id,
              len(players),
              random_seed,
              room_info)
        random.seed(random_seed)

    def got_realm_info(self, result):
        print u"你进入了%s，\n大区信息：%s" % (result['realm_name'], result['realm_info'])
        print u"所有房间列表: %s" %(str(result['rooms']),)
        self.rooms = []
        for i in result['rooms']:
            self.rooms.append((i['room_id'],i['room_name'],i['room_size']))
            print i['room_name']
        print self.rooms[0][0]
        print self.rooms
        self.join_room(self.rooms[0][0])

    def leave_room(self):
        return self.callRemote(LeaveRoom).addCallback(self.left_room).addErrback(global_no_err_back)
    def left_room(self):
        pass

class GameClientFactory(ClientFactory):

    protocol = GameClientProtocol

    def __init__(self):
        self.realm = Realm()
        self.realm.add_room(Room(u"游戏1",[],15)) # name, players, size
        pass

    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        return proto

    def trans_finished(self):
        pass

    def clientConnectionFailed(self, connector, reason):
        print 'Failed to connect to:', connector.getDestination()
        self.trans_finished()

def identify_hasher(encoded):
    """
    Returns an instance of a loaded password hasher.
    Identifies hasher algorithm by examining encoded hash, and calls
    get_hasher() to return hasher. Raises ValueError if
    algorithm cannot be identified, or if hasher is not loaded.
    """
    ## Ancient versions of Django created plain MD5 passwords and accepted
    ## MD5 passwords with an empty salt.
    #if ((len(encoded) == 32 and '$' not in encoded) or
    #        (len(encoded) == 37 and encoded.startswith('md5$$'))):
    #    algorithm = 'unsalted_md5'
    ## Ancient versions of Django accepted SHA1 passwords with an empty salt.
    #elif len(encoded) == 46 and encoded.startswith('sha1$$'):
    #    algorithm = 'unsalted_sha1'
    #else:
    #    algorithm = encoded.split('$', 1)[0]
    algorithm = encoded.split('$', 1)[0]
    return get_hasher(algorithm)


