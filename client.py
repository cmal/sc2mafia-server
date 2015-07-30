#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.internet import wxreactor
wxreactor.install()
import wx,sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from startpage.window import StartpageWindow
from twisted.internet.protocol import ClientFactory
from login import LoginDialog
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory
from network import GameClientProtocol

class ConnectionNotificationWrapper(ProtocolWrapper):
    """
    A protocol wrapper which fires a Deferred when the connection is made.
    """
    def makeConnection(self, transport):
        """
        Fire the Deferred at C{self.factory.connectionNotification} with the
        real protocol.
        """
        ProtocolWrapper.makeConnection(self, transport)
        self.factory.connectionNotification.callback(self.wrappedProtocol)

class ConnectionNotificationFactory(WrappingFactory):
    """
    A factory which uses L{ConnectionNotificationWrapper}.
    @ivar connectionNotification: The Deferred which will be fired with a
    Protocol at some point.
    """
    protocol = ConnectionNotificationWrapper

    def __init__(self, realFactory):
        WrappingFactory.__init__(self, realFactory)
        self.connectionNotification = Deferred()




class Sc2mafiaApp(wx.App):
    """Application class for the sc2mafia application."""

    def OnInit(self):
        self.frame = StartpageWindow(None, -1, u"sc2mafia",
                wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.login_window = LoginDialog(self.frame, -1, u'注册/登陆')
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        host = 'localhost'
        port = 10000
        self.d = self.connect(host, port)
        self.login()

        log.msg('Initialized')
        # OnInit must return a boolean
        return True

    def connect(self, host, port):
        clientFactory = ClientFactory()
        clientFactory.protocol = lambda: GameClientProtocol()
        factory = ConnectionNotificationFactory(clientFactory)
        reactor.connectTCP(host, port, factory)
        return factory.connectionNotification
        
    def introduce(self, protocol):
        self.protocol = protocol
        return self.protocol.introduce(self.player_name, self.password)

    def gotIntroduced(self, msg):
        if msg == 'auth failed':
            wx.MessageBox(u"密码错误",u"错误")
            self.login()
        if msg == 'null player_name or null password':
            wx.MessageBox(u"用户名或密码不能为空",u"错误")
            self.login()
        if msg == 'player created':
            wx.MessageBox(u"新建用户",u"")
        if msg == 'player authed':
            wx.MessageBox(u"验证通过",u"")

    def login(self):
        #self.frm = self.GetTopWindow()  # self.frm == self.frame
        if self.login_window.ShowModal() == wx.ID_OK:
            self.player_name = self.login_window.user #unicode
            self.password = self.login_window.password #unicode
        self.d.addCallback(self.introduce)
        self.d.addCallback(self.gotIntroduced)
        self.login_window.Destroy()

def game_client_main():
    # register the App instance with Twisted:
    app = Sc2mafiaApp(0)
    reactor.registerWxApp(app)
    reactor.run()


if __name__ == '__main__':
    game_client_main()
