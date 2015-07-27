# -*- test-case-name: test.test_game -*-

class Gossip(object):
    """
    used by both server and client.
    """
    def __init__(self, player=None, phase=None, legal=False, visibles=[]):
        """
        Create a Gossip object.
        @ivar player: the player who send this gossip.
        @type player: L{Player}
        @ivar server_time: stamp the server time when being send to the server.
        @type server_time: float, server will use Time.time() to get it.
        @ivar phase: the game phase since started.
        @type phase: L{Phase}
        @ivar legal: whether this gossip is legal to send
        @type legal: bool
        @ivar visibles: the visible list, who will this gossip be sent to.
        """
        self.player = player
        self.server_time = 0
        self.phase = phase
        self.legal = False
        self.visibles = []

