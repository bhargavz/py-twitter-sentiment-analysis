#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: friendObj.py
#
#   An object that mirrors the friends table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
import copy

class friendObj(object):
    def __init__(self):
        self.rid = None
        self.user = u""
        self.friend = u""
        self.user_id = 0
        self.friend_id = 0
        self.user_local_id = 0
        self.friend_local_id = 0


    def to_dict(self):
        rec = {}
        if( self.rid > 0 ):
            rec['rid'] = self.rid
        rec['user'] = self.user
        rec['friend'] = self.friend
        rec['user_id'] = self.user_id
        rec['friend_id'] = self.friend_id
        rec['user_local_id'] = self.user_local_id        
        rec['friend_local_id'] = self.friend_local_id
        return rec

    def from_dict(self, rec):
        nobj = friendObj()
        if( rec ):
            nobj.user = rec['user']
            nobj.friend = rec['friend']
            nobj.user_id = rec['user_id']
            nobj.friend_id = rec['friend_id']
            nobj.user_local_id = rec['user_local_id']
            nobj.friend_local_id = rec['friend_local_id']
        return nobj

    def clone(self):
        nobj = friendObj()
        if( self.rid > 0 ):
            nobj.rid = self.rid
        nobj.user = self.user
        nobj.friend = self.friend
        nobj.user_id = self.user_id
        nobj.friend_id = self.friend_id
        nobj.user_local_id = self.user_local_id
        nobj.friend_local_id = self.friend_local_id
        return nobj

    def __repr__(self):
        return "<friendObj('%s','%s','%s','%s','%s','%s','%s')>"%(str(self.rid),str(self.user),str(self.friend),str(self.user_id),str(self.friend_id),str(self.user_local_id),str(self.friend_local_id))

