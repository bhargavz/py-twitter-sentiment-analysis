#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: userObj.py
#
#   An object that mirrors the user data table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from datetime import datetime
import copy

class userObj(object):
    def __init__(self):
        self.rid = None
        self.user_name = ""
        self.screen_name = ""
        self.user_id = 0
        self.join_dt = datetime(2000,1,1,0,0,0,0)
        self.verified = False
        self.geo_enabled = False
        self.location = ""
        self.lang = ""
        self.time_zone = ""
        self.url = ""
        self.description = ""


    def to_dict(self):
        rec = {}
        if( self.rid > 0 ):
            rec['rid'] = self.rid
        rec['user_name'] = self.user_name
        rec['screen_name'] = self.screen_name
        rec['user_id'] = self.user_id
        rec['join_dt'] = self.join_dt
        rec['verified'] = self.verified        
        rec['geo_enabled'] = self.geo_enabled        
        rec['location'] = self.location
        rec['lang'] = self.lang
        rec['time_zone'] = self.time_zone
        rec['url'] = self.url
        rec['description'] = self.description
        return rec

    def from_dict(self, rec):
        nobj = userObj()
        if( rec ):
            nobj.user_name = rec['user_name']
            nobj.screen_name = rec['screen_name']
            nobj.user_id = rec['user_id']
            nobj.join_dt = rec['join_dt']
            nobj.verified = rec['verified']
            nobj.geo_enabled = rec['geo_enabled']
            nobj.location = rec['location']
            nobj.lang = rec['lang']
            nobj.time_zone = rec['time_zone']
            nobj.url = rec['url']
            nobj.description = rec['description']
        return nobj

    def clone(self):
        nobj = userObj()
        if( self.rid > 0 ):
            nobj.rid = self.rid
        nobj.user_name = self.user_name
        nobj.screen_name = self.screen_name
        nobj.user_id = self.user_id
        nobj.join_dt = self.join_dt
        nobj.verified = self.verified
        nobj.geo_enabled = self.geo_enabled
        nobj.location = self.location
        nobj.lang = self.lang
        nobj.time_zone = self.time_zone
        nobj.url = self.url
        nobj.description = self.description
        return nobj

    def __repr__(self):
        return "<userObj('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>"%(str(self.rid),str(self.user_name),str(self.screen_name),str(self.user_id),str(self.join_dt),str(self.verified),str(self.geo_enabled),str(self.location),str(self.lang),str(self.time_zone),str(self.url),str(self.description))

