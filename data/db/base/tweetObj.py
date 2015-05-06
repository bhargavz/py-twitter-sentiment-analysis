#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: tweetObj.py
#
#   An object that mirrors the tweets table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from datetime import datetime
import copy

class tweetObj(object):
    def __init__(self):
        self.rid = None
        self.tweet_id = 0
        self.tweet_id_str = ""
        self.created_at = datetime(2000,1,1,0,0,0,0)
        self.from_user_id = long(0)
        self.from_user = ""
        self.from_user_name = ""
        self.lat = 0.0
        self.lon = 0.0
        self.tweet_text = ""


    def to_dict(self):
        rec = {}
        if( self.rid > 0 ):
            rec['rid'] = self.rid
        rec['tweet_id'] = self.tweet_id
        rec['created_at'] = self.created_at
        rec['tweet_id_str'] = self.tweet_id_str
        rec['lat'] = self.lat
        rec['lon'] = self.lon
        rec['from_user'] = self.from_user
        rec['from_user_name'] = self.from_user_name        
        rec['from_user_id'] = self.from_user_id        
        rec['tweet_text'] = self.tweet_text
        return rec

    def from_dict(self, rec):
        nobj = tweetObj()
        if( rec ):
            nobj.tweet_id = rec['tweet_id']
            nobj.created_at = rec['created_at']
            nobj.tweet_id_str = rec['tweet_id_str']
            nobj.lat = rec['lat']
            nobj.lon = rec['lon']
            nobj.from_user = rec['from_user']
            nobj.from_user_name = rec['from_user_name']
            nobj.from_user_id = rec['from_user_id']
            nobj.tweet_text = rec['tweet_text']
        return nobj

    def clone(self):
        nobj = tweetObj()
        if( self.rid > 0 ):
            nobj.rid = self.rid
        nobj.tweet_id = self.tweet_id
        nobj.created_at = self.created_at
        nobj.tweet_id_str = self.tweet_id_str
        nobj.lat = self.lat
        nobj.lon = self.lon
        nobj.from_user = self.from_user
        nobj.from_user_name = self.from_user_name
        nobj.from_user_id = self.from_user_id
        nobj.tweet_text = self.tweet_text
        return nobj

    def __repr__(self):
        return "<tweetObj('%s','%s','%s','%s','%s','%s','%s')>"%(str(self.rid),str(self.tweet_id),str(self.created_at),str(self.from_user),str(self.from_user_name),str(self.from_user_id),str(self.tweet_text))

