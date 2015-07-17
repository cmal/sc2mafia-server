# This is the Twisted Fast Poetry Server, version 2.0

from twisted.application import internet, service
from twisted.internet.protocol import ServerFactory, Protocol
from twisted.python import log

# Normally we would import these classes from another module.

# class PoetryProtocol(Protocol):

#     def connectionMade(self):
#         poem = self.factory.service.poem
#         log.msg('sending %d bytes of poetry to %s'
#                 % (len(poem), self.transport.getPeer()))
#         self.transport.write(poem)
#         self.transport.loseConnection()


# class PoetryFactory(ServerFactory):

#     protocol = PoetryProtocol

#     def __init__(self, service):
#         self.service = service


# class PoetryService(service.Service):

#     def __init__(self, welcome_file):
#         self.welcome_file = welcome_file

#     def startService(self):
#         service.Service.startService(self)
#         self.poem = open(self.welcome_file).read()
#         log.msg('loaded a poem from: %s' % (self.welcome_file,))


# configuration parameters
port = 10000
iface = 'localhost'
welcome_file = 'welcome.txt'

# this will hold the services that combine to form the poetry server
top_service = service.MultiService()

# the poetry service holds the poem. it will load the poem when it is
# started
poetry_service = PoetryService(welcome_file)
poetry_service.setServiceParent(top_service)

# the tcp service connects the factory to a listening socket. it will
# create the listening socket when it is started
factory = PoetryFactory(poetry_service)
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(top_service)

# this variable has to be named 'application'
application = service.Application("sc2mafia")

# this hooks the collection we made to the application
top_service.setServiceParent(application)

# at this point, the application is ready to go. when started by
# twistd it will start the child services, thus starting up the
# poetry server
