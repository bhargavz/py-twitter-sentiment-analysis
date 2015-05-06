#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleTweetsDB.py
#
#   An object for managing the fitness tweet collection
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.TweetsDB import TweetsDB
from sochi.data.db.sochi.ExampleTweetObj import ExampleTweetObj
from sochi.data.db.sochi.ExampleUserObj import ExampleUserObj
from sochi.data.db.sochi.ExampleUserMetaObj import ExampleUserMetaObj
from sochi.data.db.sochi.ExampleFollowerObj import ExampleFollowerObj
from sochi.data.db.sochi.ExampleFriendObj import ExampleFriendObj
from sqlalchemy.orm import mapper, class_mapper
from sqlalchemy.orm.exc import UnmappedClassError
import sys

class ExampleTweetsDB(TweetsDB):
    def __init__(self, config=None):
        TweetsDB.__init__(self, config=config)

        try:
            self.tweet_mapper = class_mapper(ExampleTweetObj)
        except UnmappedClassError:
            self.tweet_mapper = mapper(ExampleTweetObj,self.tweet_table)

        try:
            self.user_mapper = class_mapper(ExampleUserObj)
        except UnmappedClassError:
            self.user_mapper = mapper(ExampleUserObj,self.user_table)

        try:
            self.user_meta_mapper = class_mapper(ExampleUserMetaObj)
        except UnmappedClassError:
            self.user_meta_mapper = mapper(ExampleUserMetaObj,self.user_meta_table)

        try:
            self.friend_mapper = class_mapper(ExampleFriendObj)
        except UnmappedClassError:
            self.friend_mapper = mapper(ExampleFriendObj,self.friends_table)

        try:
            self.follower_mapper = class_mapper(ExampleFollowerObj)
        except UnmappedClassError:
            self.follower_mapper = mapper(ExampleFollowerObj,self.followers_table)


##
# New object creation routines
##
    ## Create "tweet" objects and records
    def new_tweet_table_item(self, rec=None):
        nto = ExampleTweetObj()
        if( rec ):
            return nto.from_dict(rec)
        return nto

    def tweet_table_item_to_dict(self, tto=None):
        rec = {}
        if( tto ):
            rec = tto.to_dict()
        return rec

    ## Create "user" objects and records
    def new_user_table_item(self, rec=None):
        uto = ExampleUserObj()
        if( rec ):
            return uto.from_dict(rec)
        return uto
        
    def user_table_item_to_dict(self, uto=None):
        rec = {}
        if( uto ):
            rec = uto.to_dict()
        return rec

    ## Create "user_meta" objects and records
    def new_user_meta_table_item(self, rec=None):
        umto = ExampleUserMetaObj()
        if( rec ):
            return umto.from_dict(rec)
        return umto
        
    def user_meta_table_item_to_dict(self, umto=None):
        rec = {}
        if( umto ):
            rec = umto.to_dict()
        return rec
        
    ## Create "friend" objects and records
    def new_friend_table_item(self, rec=None):
        nf = ExampleFriendObj()
        if( rec ):
            return nf.from_dict(rec)
        return nf
        
    def friend_table_item_to_dict(self, nf=None):
        rec = {}
        if( nf ):
            rec = nf.to_dict()
        return rec

    ## Create "follower" objects and records
    def new_follower_table_item(self, rec=None):
        nf = ExampleFollowerObj()
        if( rec ):
            return nf.from_dict(rec)
        return nf
        
    def follower_table_item_to_dict(self, nf=None):
        rec = {}
        if( nf ):
            rec = nf.to_dict()
        return rec

##
# straight forward query types
##
    ##
    ## Query the tweet table
    ##
    def query_tweet_table_by_tweet_id(self, tid):
        t = self.session.query(ExampleTweetObj).filter(ExampleTweetObj.tweet_id==tid).all()
        return t

    def query_tweet_table_by_username(self, uname=None, start_date=None, end_date=None):
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(ExampleTweetObj.from_user==uname)
        tlist = q.all()
        return tlist

    def query_tweet_table_by_user_id(self, uid=None, start_date=None, end_date=None):
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(ExampleTweetObj.from_user_id==uid)
        tlist = q.all()
        return tlist

    def query_tweet_table_by_tweet_substr(self, substr=None, start_date=None, end_date=None):
        qtext = "%"+substr+"%"
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(ExampleTweetObj.tweet_text.like(qtext))
        tlist = q.all()
        return tlist

    def _tweet_table_date_range(self, start_date=None, end_date=None):
        query = self.session.query(ExampleTweetObj)
        if( start_date and end_date ):
            query = query.filter(ExampleTweetObj.created_at>=start_date)
            query = query.filter(ExampleTweetObj.created_at<end_date)
        elif( start_date ):
            query = query.filter(ExampleTweetObj.created_at>=start_date)
        elif( end_date ):
            query = query.filter(ExampleTweetObj.created_at<end_date)
        else:
            pass
        return query

    ##
    ## Query the user table
    ##
    def query_user_table_by_record_id(self, rid=None, rid2=None):
        if( rid2 ):
            q = self.session.query(ExampleUserObj).filter(ExampleUserObj.rid>=rid)
            tlist = q.filter(ExampleUserObj.rid<rid2).all()
        else:
            tlist = self.session.query(ExampleUserObj).filter(ExampleUserObj.rid==rid).all()
        return tlist
        
    def query_user_table_by_fullname(self, sname):
        tlist = self.session.query(ExampleUserObj).filter(ExampleUserObj.screen_name==sname).all()
        return tlist

    def query_user_table_by_screenname(self, sname):
        tlist = self.session.query(ExampleUserObj).filter(ExampleUserObj.screen_name==sname).all()
        return tlist

    def query_user_table_by_username(self, uname):
        tlist = self.session.query(ExampleUserObj).filter(ExampleUserObj.user_name==uname).all()
        return tlist

    def query_user_table_by_user_id(self, uid):
        tlist = self.session.query(ExampleUserObj).filter(ExampleUserObj.user_id==uid).all()
        return tlist


    ##
    ## Query the user_meta table
    ##
    def query_user_meta_table_by_fullname(self, sname):
        tlist = self.session.query(ExampleUserMetaObj).filter(ExampleUserMetaObj.screen_name==sname).all()
        return tlist

    def query_user_meta_table_by_screenname(self, sname):
        tlist = self.session.query(ExampleUserMetaObj).filter(ExampleUserMetaObj.screen_name==sname).all()
        return tlist

    def query_user_meta_table_by_username(self, uname):
        tlist = self.session.query(ExampleUserMetaObj).filter(ExampleUserMetaObj.user_name==uname).all()
        return tlist

    def query_user_meta_table_by_user_id(self, uid):
        tlist = self.session.query(ExampleUserMetaObj).filter(ExampleUserMetaObj.user_id==uid).all()
        return tlist


    ##
    ## Query the friends table
    ##
    def query_friends_by_username(self, uname=None, fname=None):
        q = self.session.query(ExampleFriendObj).filter(ExampleFriendObj.user==uname)
        if( fname ):
            q = q.filter(ExampleFriendObj.friend==fname)
        flist = q.all()
        return flist

    def query_friends_by_user_id(self, uid=None, fid=None):
        q = self.session.query(ExampleFriendObj).filter(ExampleFriendObj.user_id==uid)
        if( fid ):
            q = q.filter(ExampleFriendObj.friend_id==fid)
        flist = q.all()
        return flist


    ##
    ## Query the followers table
    ##
    def query_followers_by_username(self, uname=None, fname=None):
        q = self.session.query(ExampleFollowerObj).filter(ExampleFollowerObj.user==uname)
        if( fname ):
            q = q.filter(ExampleFollowerObj.follower==fname)
        flist = q.all()
        return flist

    def query_followers_by_user_id(self, uid=None, fid=None):
        q = self.session.query(ExampleFollowerObj).filter(ExampleFollowerObj.user_id==uid)
        if( fid ):
            q = q.filter(ExampleFollowerObj.follower_id==fid)
        flist = q.all()
        return flist


