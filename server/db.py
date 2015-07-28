#!/usr/bin/env python
# -*- coding: utf-8 -*-
import anydbm

class UserDb(object):
    def __init__(self):
        # Open database, creating it if necessary.
        self.db = anydbm.open('userpass.txt', 'c')
        self.users = {}
        for k, v in self.db.iteritems():
            self.users[k] = v

    def add_user(self, user, password):
        self.users[user] = password

    def get_password(self, user):
        return self.users[user]

    def __del__(self):
        self.db.close()
