#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: userMetaObj.py
#
#   An object that mirrors the user meta data table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from datetime import datetime
import copy

class userMetaObj(object):
    def __init__(self):
        self.rid = None
        self.user_name = ""
        self.screen_name = ""
        self.user_id = 0
        self.friend_count = 0
        self.follower_count = 0
        self.profile_collect_dt = datetime(2000,1,1,0,0,0,0)
        self.friend_collect_dt = datetime(2000,1,1,0,0,0,0)
        self.friend_collect_resp = ""
        self.follower_collect_dt = datetime(2000,1,1,0,0,0,0)
        self.follower_collect_resp = ""


    def to_dict(self):
        rec = {}
        if( self.rid > 0 ):
            rec['rid'] = self.rid
        rec['user_name'] = self.user_name
        rec['screen_name'] = self.screen_name
        rec['user_id'] = self.user_id
        rec['friend_count'] = self.friend_count
        rec['follower_count'] = self.follower_count
        rec['profile_collect_dt'] = self.profile_collect_dt
        rec['friend_collect_dt'] = self.friend_collect_dt
        rec['friend_collect_resp'] = self.friend_collect_resp
        rec['follower_collect_dt'] = self.follower_collect_dt
        rec['follower_collect_resp'] = self.follower_collect_resp
        return rec

    def from_dict(self, rec):
        nobj = userObj()
        if( rec ):
            nobj.user_name = rec['user_name']
            nobj.screen_name = rec['screen_name']
            nobj.user_id = rec['user_id']
            nobj.friend_count = rec['friend_count']
            nobj.follower_count = rec['follower_count']
            nobj.profile_collect_dt = rec['profile_collect_dt']
            nobj.friend_collect_dt = rec['friend_collect_dt']
            nobj.friend_collect_resp = rec['friend_collect_resp']
            nobj.follower_collect_dt = rec['follower_collect_dt']
            nobj.follower_collect_resp = rec['follower_collect_resp']
        return nobj

    def clone(self):
        nobj = userObj()
        if( self.rid > 0 ):
            nobj.rid = self.rid
        nobj.user_name = self.user_name
        nobj.screen_name = self.screen_name
        nobj.user_id = self.user_id
        nobj.friend_count = self.friend_count
        nobj.follower_count = self.follower_count
        nobj.profile_collect_dt = self.profile_collect_dt
        nobj.friend_collect_dt = self.friend_collect_dt
        nobj.friend_collect_resp = self.friend_collect_resp
        nobj.follower_collect_dt = self.follower_collect_dt
        nobj.follower_collect_resp = self.follower_collect_resp
        return nobj

    def __repr__(self):
        return "<userMetaObj('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',)>"%(str(self.rid),str(self.user_name),str(self.screen_name),str(self.user_id),str(self.friend_count),str(self.follower_count),str(self.profile_collect_dt),str(self.friend_collect_dt),str(self.friend_collect_resp),str(self.follower_collect_dt),str(self.follower_collect_resp))

