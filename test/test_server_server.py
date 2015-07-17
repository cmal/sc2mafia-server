from server.server import PoetryFactory
from twisted.trial import unittest


class PoetryClientProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)


class PoetryClientProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)

def get_poetry(host, port):
    from twisted.internet import reactor
    factory = PoetryClientFactory()
    reactor.connectTCP(host, port, factory)
    return factory.deferred

wf = "welcome.txt"

class PeotryTestCase(unittest.TestCase):
    def setUp(self):
        send_data = open(wf).read()
        factory = PoetryFactory(content)
        from twisted.internet import reactor
        self.port = reactor.listenTCP(0, factory, interface="127.0.0.1")
        self.portnum = self.port.getHost().port

    def tearDown(self):
        port, self.port = self.port, None
        return port.stopListening()

    def test_client(self):
        """The correct poem is returned by get_poetry."""
        d = get_poetry('127.0.0.1', self.portnum)

        def got_poem(rcv_data):
            self.assertEquals(rcv_data, send_data)

        d.addCallback(got_poem)

        return d

    def test_failure(self):
        """The correct failure is returned by get_poetry when
        connecting to a port with no server."""
        d = get_poetry('127.0.0.1', 0)
        return self.assertFailure(d, ConnectError)

