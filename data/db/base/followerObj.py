#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: followersObj.py
#
#   An object that mirrors the followers table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
import copy

class followerObj(object):
    def __init__(self):
        self.rid = None
        self.user = u""
        self.follower = u""
        self.user_id = 0
        self.follower_id = 0
        self.user_local_id = 0
        self.follower_local_id = 0


    def to_dict(self):
        rec = {}
        if( self.rid > 0 ):
            rec['rid'] = self.rid
        rec['user'] = self.user
        rec['follower'] = self.follower
        rec['user_id'] = self.user_id
        rec['follower_id'] = self.follower_id
        rec['user_local_id'] = self.user_local_id        
        rec['follower_local_id'] = self.follower_local_id
        return rec

    def from_dict(self, rec):
        nobj = followerObj()
        if( rec ):
            nobj.user = rec['user']
            nobj.follower = rec['follower']
            nobj.user_id = rec['user_id']
            nobj.follower_id = rec['follower_id']
            nobj.user_local_id = rec['user_local_id']
            nobj.follower_local_id = rec['follower_local_id']
        return nobj

    def clone(self):
        nobj = followerObj()
        if( self.rid > 0 ):
            nobj.rid = self.rid
        nobj.user = self.user
        nobj.follower = self.follower
        nobj.user_id = self.user_id
        nobj.follower_id = self.follower_id
        nobj.user_local_id = self.user_local_id
        nobj.follower_local_id = self.follower_local_id
        return nobj

    def __repr__(self):
        return "<followersObj('%s','%s','%s','%s','%s','%s','%s')>"%(str(self.rid),str(self.user),str(self.follower),str(self.user_id),str(self.follower_id),str(self.user_local_id),str(self.follower_local_id))

