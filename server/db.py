#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.python import log
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Unicode

from sqlalchemy import create_engine
engine = create_engine('sqlite:///game.db', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
SessionMaker = sessionmaker(bind=engine)



class User(Base):
     __tablename__ = 'users'
     id = Column(Integer, primary_key=True)
     name = Column(Unicode, nullable=False, unique=True)
     password = Column(Unicode, nullable=False)
     def __init__(self, name, password):
         self.name = name
         self.password = password
     def __repr__(self):
        return "<User(name='%s', password='%s')>" % (
                             self.name, self.password)


from sqlalchemy.exc import OperationalError
try:
    Base.metadata.create_all(engine)
except OperationalError:
    import wx
    wx.MessageBox(u"无法连接服务器,本程序将退出",u"错误")
    raise SystemExit

