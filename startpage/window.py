#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==============================================================================
#
# This file is a part of Human Resource System of BQD Jinan Branch.
#
# File: HRSLib\window.py
# Description: Central file for all HRS GUI code.
# Author: Yu Zhao 赵宇 <zyzy5730@163.com>
#
# Copyright (C) 2012-2013 Yu Zhao.
#
#==============================================================================

import os
import wx

class StartpageWindow(wx.Frame):
    """Main class of sc2mafia the start page, the create game page.
    All GUI logic is here.
    """

    def __init__(self, parent, id, title, style):
        """Construct the GUI from config file, and bind GUI events to
        their handlers.

        """
        # 读取sc2mafia.cfg
        self.readFromCfg()
        # 调用基类的构造函数
        wx.Frame.__init__(self, parent, wx.ID_ANY, title,
                size=self.framesize, style=style)

        self.app = wx.GetApp()
        #self.protocol = parent.factory.protocol
        #print self.protocol
        # 加载资源
        #self.resin = Resin(os.path.join(homepath,
        #        'res', self.prefer.getValue("iconset")))
        #self.resin = Resin()
        # 图标
        #self.SetIcon(self.resin.getIcon("notalon"))
        # 提示
        #self.tips = wx.CreateFileTipProvider("Tips.txt", 0)
        #self.showtips = int(self.config.get("other", "showtips"))
#        if self.showtips:
#            wx.CallAfter(self.ShowTips)  # 显示Tips的同时显示主界面
#                int(self.config.get("frame","height")))
            # self.ShowTips()  # 与上面相反，显示Tips之后才显示主界面
        # 创建MenuBar
        self.createMenuBar()
        # 创建ToolBar
        #self.createToolBar()
        # 创建StatusBar
        self.createStatusBar()
        # 创建主显示栏
        self.createMainWindow()
        # 绑定关闭窗口的方法
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        # 创建TaskBarIcon
        self.tbIcon = tbIcon(self)

    # -----------------创建主框架的相关函数------------------ #
    def readFromCfg(self):
        """读取配置文件

        """
        #self.config = Config(os.path.join(homepath, "sc2mafia.cfg"))
        #self.framesize = (int(self.config.get("frame","width")),
        #        int(self.config.get("frame","height")))
        self.framesize = (800,600)

    def menuData(self):
        """菜单项数据

        """
        return ((u"程序",
                    (u"退出", u"退出程序", self.OnCloseWindow)),
                (u"员工档案",
                    (u"新建", u"在远程服务器新建一个员工档案", self.OnCreateStaff),
                    (u"修改", u"修改一个员工档案", self.OnModifyStaff),
                    (u"查看", u"查看所有员工档案", self.OnDisplayStaff),
                    (u"筛选", u"筛选员工档案", self.OnFilterStaff)),
                (u"工资",
                    (u"工资单发送", "用邮件发送工资单", self.OnMailSalary),
                    ),
                (u"其他",
                    (u"报销系统", u"在这里登录报销系统", self.OnOpenExpAccHtml)),
                (u"工具",
                    (u"通讯录", u"快速查询通讯录的小工具", self.OnSearchAddr)),
                (u"帮助",
                    (u"用户手册", u"用户手册", self.OnManual),
                    ("", "", ""),
                    (u"版权", u"本软件的版权信息", self.OnCopyRight),
                    (u"关于作者", u"本软件作者的相关信息", self.OnAuthor),
                    (u"关于本软件", u"本软件的相关信息", self.OnAbout)),
                )

    def createMenuBar(self):
        """创建菜单栏

        """
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
            self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        """创建一个菜单 --从创建菜单栏函数中抽象出来的函数

        """
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def toolBarData(self):
        """工具栏数据

        """
        return ((u"创建", "new.bmp", u"新建一个员工档案", self.OnCreateStaff),
#                (u"修改", self.OnModifyStaff),
                (u"查看", "display.bmp", u"浏览", self.OnDisplayStaff),
                (u"筛选", "search.bmp", u"筛选", self.OnFilterStaff),
                ("", "", "", ""),
                (u"通讯录", "addr.bmp", u"搜索通讯录", self.OnSearchAddr),
               )

    def createToolBar(self):
        """创建工具栏

        """
        toolBar = self.CreateToolBar()
        for each in self.toolBarData():
            self.createSimpleTool(toolBar, *each)
        toolBar.Realize()

    def createSimpleTool(self, toolbar, label, filename, help, handler):
        """创建一个工具按钮  --从创建工具栏函数中抽象出来的函数

        """
        if not label:
            toolbar.AddSeparator()
            return
        bmp = wx.Image(filename, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        tool = toolbar.AddSimpleTool(-1, bmp, label, help)
        self.Bind(wx.EVT_MENU, handler, tool)

    def createMainWindow(self):
        """创建主显示窗口

        """
        panel = wx.Panel(self)
        #创建open，save按钮
        bt_send = wx.Button(panel,label=u'发送')
        bt_send.Bind(wx.EVT_BUTTON, self.OnSendMsg)
        #创建文本域，文本框
        self.rtext_chatlog = wx.TextCtrl(panel,style=wx.TE_MULTILINE|wx.VSCROLL|wx.TE_RICH2)
        self.rtext_chatlog.SetEditable(False)
        self.text_send = wx.TextCtrl(panel)
        self.text_send.SetFocus()
        #添加布局管理器
        bsizer_bottom = wx.BoxSizer()
        bsizer_bottom.Add(self.text_send,proportion=1,flag=wx.EXPAND)
        bsizer_bottom.Add(bt_send,proportion=0,flag=wx.LEFT,border=5)
        bsizer_all = wx.BoxSizer(wx.VERTICAL)        #wx.VERTICAL 横向boxsizer
        bsizer_all.Add(self.rtext_chatlog,proportion=1,flag=wx.EXPAND|wx.ALL,border=5)
        bsizer_all.Add(bsizer_bottom,proportion=0,flag=wx.EXPAND|wx.LEFT,border=5)
 
        panel.SetSizer(bsizer_all)
        pass

    # 显示每日提示
#    def ShowTips(self):
#        """Shows the tips window on startup; returns False if the option to
#        turn off tips is checked.
#
#        """
#        # constructs the tip (wx.ShowTip), which returns whether or not the
#        # user checked the 'show tips' box
#        if wx.ShowTip(None, self.tips, True):
#            btmp = 1
#            print 1
#        else:
#            btmp = 0
#            print 0
#        self.config.set("other", "showtips", btmp)
#        return self.config.get("other", "showtips")

    # 发送聊天消息
    def OnSendMsg(self, event):
        chat = self.text_send.GetValue() # <= is unicode
        self.rtext_chatlog.AppendText(chat)
        self.rtext_chatlog.AppendText(os.linesep)
        self.text_send.Clear()
        self.text_send.SetFocus()
        pass

    # ----------------------主框架的事件响应函数------------------------#
    def OnCreateStaff(self, event):
        pass

    def OnModifyStaff(self, event):
        pass

    def OnDisplayStaff(self, event):
        pass

    def OnFilterStaff(self, event):
        pass

    def OnMailSalary(self, event):
        pass

    def OnOpenExpAccHtml(self, event):
        pass

    def OnSearchAddr(self, event):
        pass

    def OnManual(self, event):
        pass

    def OnCopyRight(self, event):
        pass

    def OnAuthor(self, event):
        pass

    def OnAbout(self, event):
        pass

    def createStatusBar(self):
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-1, -2, -3])

    # Sash位置变动
    def OnSashPosChanged(self, event):
        """Handler for when the splitter sash,
        who divided the `tree` and the `content`, is moved.

        """
        pass
#        pos = self.splitter.GetSashPosition()
#        self.config.setValue("sashposition", pos)

    def OnSelChanged(self):
        pass

    # 关闭主框架，清理资源 # TODO:devo
    def OnCloseWindow(self, event):
        self.tbIcon.Destroy()
        self.Destroy()


class tbIcon(wx.TaskBarIcon):
    ID_HIDE = wx.NewId()
    ID_SHOW = wx.NewId()
    ID_EXIT = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        #self.SetIcon(self.frame.resin.getIcon("notalon"))
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
#        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.CreatePopupMenu)
        self.Bind(wx.EVT_MENU, self.onHide, id=self.ID_HIDE)
        self.Bind(wx.EVT_MENU, self.onShow, id=self.ID_SHOW)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()
        else:
            self.frame.Show(False)

    def onHide(self, event):
        if self.frame.IsShown():
            self.frame.Show(False)

    def onShow(self, event):
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def onExit(self, event):
        self.frame.Close()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_SHOW, u"显示主窗口")
        menu.Append(self.ID_HIDE, u"隐藏主窗口")
        menu.AppendSeparator()
        menu.Append(self.ID_EXIT, u"退出程序")
        return menu
