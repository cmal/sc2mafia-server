from server.server import PoetryFactory, PoetryService
from twisted.trial import unittest
from twisted.internet.protocol import Protocol, ClientFactory, ServerFactory
from twisted.internet.defer import Deferred
from twisted.internet.error import ConnectError
from echo_client import EchoClientFactory

class PoetryClientProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)

class PoetryClientFactory(ClientFactory):

    protocol = PoetryClientProtocol

    def __init__(self):
        self.deferred = Deferred()

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

def get_poetry(host, port):
    from twisted.internet import reactor
    factory = PoetryClientFactory()
    reactor.connvectTCP(host, port, factory)
    return factory.deferred


class PeotryTestCase(unittest.TestCase):

    def setUp(self):
        self.wf = "../welcome.txt"
        self.send_data = open(self.wf).read()
        self.service = PoetryService(self.wf)
        factory = PoetryFactory(self.service)
        from twisted.internet import reactor
        self.port = reactor.listenTCP(0, factory, interface="127.0.0.1")
        self.portnum = self.port.getHost().port

    def tearDown(self):
        port, self.port = self.port, None
        return port.stopListening()

    def test_client(self):
        """The correct poem is returned by get_poetry."""
        self.service.startService()
        d = get_poetry('127.0.0.1', self.portnum)

        def got_poem(poem):
            self.assertEquals(poem, self.send_data)

        d.addCallback(got_poem)

        return d

    def test_failure(self):
        """The correct failure is returned by get_poetry when
        connecting to a port with no server."""
        d = get_poetry('127.0.0.1', 0)
        return self.assertFailure(d, ConnectError)

def echo_line(host, port):
    from twisted.internet import reactor
    factory = EchoClientFactory()
    reactor.connectTCP(host, port, factory)
    return factory.deferred

class EchoProtocol(Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(ServerFactory):
    protocol = EchoProtocol
    pass

class EchoTestCase(UnitTest.TestCase):

    def setUp(self):
        
        
    def test_echo_client(self):
        
