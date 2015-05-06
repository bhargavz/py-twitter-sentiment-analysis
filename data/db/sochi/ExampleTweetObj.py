#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleTweetObj.py
#
#   An object that mirrors the tweets table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.tweetObj import tweetObj
from datetime import datetime
import copy

class ExampleTweetObj(tweetObj):
    def __init__(self):
        tweetObj.__init__(self)
        self.query_source = ""

#    def to_dict(self):
#        rec = {}
#        if( self.rid > 0 ):
#            rec['rid'] = self.rid
#        rec['tweet_id'] = self.tweet_id
#        rec['created_at'] = self.created_at
#        rec['tweet_id_str'] = self.tweet_id_str
#        rec['lat'] = self.lat
#        rec['lon'] = self.lon
#        rec['query_source'] = self.query_source
#        rec['from_user'] = self.from_user
#        rec['from_user_name'] = self.from_user_name        
#        rec['from_user_id'] = self.from_user_id        
#        rec['tweet_text'] = self.tweet_text
#        return rec
#
#    def from_dict(self, rec):
#        nobj = ExampleTweetObj()
#        if( rec ):
#            nobj.tweet_id = rec['tweet_id']
#            nobj.created_at = rec['created_at']
#            nobj.tweet_id_str = rec['tweet_id_str']
#            nobj.lat = rec['lat']
#            nobj.lon = rec['lon']
#            nobj.query_source = rec['query_source']
#            nobj.from_user = rec['from_user']
#            nobj.from_user_name = rec['from_user_name']
#            nobj.from_user_id = rec['from_user_id']
#            nobj.tweet_text = rec['tweet_text']
#        return nobj
#
#    def clone(self):
#        nobj = ExampleTweetObj()
#        if( self.rid > 0 ):
#            nobj.rid = self.rid
#        nobj.tweet_id = self.tweet_id
#        nobj.created_at = self.created_at
#        nobj.tweet_id_str = self.tweet_id_str
#        nobj.lat = self.lat
#        nobj.lon = self.lon
#        nobj.query_source = self.query_source
#        nobj.from_user = self.from_user
#        nobj.from_user_name = self.from_user_name
#        nobj.from_user_id = self.from_user_id
#        nobj.tweet_text = self.tweet_text
#        return nobj

    def __repr__(self):
        result = "ExampleTweetObj():\n\t"
        result = result+"rid: %s\n\t"%(str(self.rid))
        result = result+"tweet_id: %s\n\t"%(str(self.tweet_id))
        result = result+"created_at: %s\n\t"%(str(self.created_at))
        result = result+"query_source: %s\n\t"%(str(self.query_source))
        result = result+"from_user: "+self.from_user.encode('utf-8')+"\n\t"
        result = result+"from_user_name: "+self.from_user_name.encode('utf-8')+"\n\t"
        result = result+"from_user_id: %d\n\t"%(self.from_user_id)
        result = result+"tweet: "+self.tweet_text.encode('utf-8')
        return result

