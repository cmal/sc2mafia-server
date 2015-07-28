#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.internet import wxreactor
wxreactor.install()
import wx,sys
from twisted.python import log
from twisted.internet import reactor
from startpage.window import StartpageWindow
from network import GameClientFactory
from login import LoginDialog

class Sc2mafiaApp(wx.App):
    """Application class for the sc2mafia application."""

    def OnInit(self):
        self.frame = StartpageWindow(None, -1, u"sc2mafia",
                wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.login_window = LoginDialog(self.frame, -1, u'登陆')
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.login_window.ShowModal()
        #self.frm = self.GetTopWindow()  # self.frm == self.frame
        self.factory = GameClientFactory()
        print type(self.login_window.user)
        print type(self.login_window.password)
        self.factory.protocol.player_name = self.login_window.user
        self.factory.password = self.login_window.password
        host = 'localhost'
        port = 10000
        reactor.connectTCP(host, port, self.factory)


        log.msg('Initialized')
        # OnInit must return a boolean
        return True


def game_client_main():

#    log.startLogging(sys.stdout)

    # register the App instance with Twisted:
    app = Sc2mafiaApp(0)
    reactor.registerWxApp(app)
    reactor.run()


if __name__ == '__main__':
    game_client_main()
