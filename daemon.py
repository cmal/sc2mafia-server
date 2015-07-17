# This is the Twisted Fast Poetry Server, version 2.0

from twisted.application import internet, service
# import these classes from another module.
from server.server import PoetryProtocol, PoetryFactory, PoetryService

# configuration parameters
port = 10000
iface = 'localhost'
welcome_file = 'welcome.txt'

# this will hold the services that combine to form the server
top_service = service.MultiService()

# create multiple services and then add to the top service
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
