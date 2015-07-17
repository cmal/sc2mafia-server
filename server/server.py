# This is the Twisted Fast Poetry Server, version 1.0

from twisted.application import service
from twisted.internet.protocol import ServerFactory, Protocol
from twisted.python import log


class PoetryProtocol(Protocol):

    def connectionMade(self):
        send_data = self.factory.service.send_data
        log.msg('sending %d bytes of peotry to %s'
                % (len(send_data), self.transport.getPeer()))
        self.transport.write(send_data)
        self.transport.loseConnection()


class PoetryFactory(ServerFactory):

    protocol = PoetryProtocol

    def __init__(self, service):
        self.service = service

class PoetryService(service.Service):

    def __init__(self, wf):  # wf, welcome file
        self.wf = wf

    def startService(self):
        service.Service.startService(self)
        self.send_data = open(self.wf).read()
        log.msg('loaded a welcome file from: %s' % (self.wf,))
