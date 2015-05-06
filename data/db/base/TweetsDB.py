#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: twitterDB.py
#
#   An object for managing a twitter DB 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.baseDB import BaseDB
from sochi.data.db.base.dbManager import DBManager
from sochi.data.db.base.tweetObj import tweetObj as TweetObj
from sochi.data.db.base.userObj import userObj
from sochi.data.db.base.userMetaObj import userMetaObj
from sochi.data.db.base.friendObj import friendObj
from sochi.data.db.base.followerObj import followerObj
from sqlalchemy.orm import mapper, class_mapper
from sqlalchemy.orm.exc import UnmappedClassError
import sys


TWEETS_TABLE_NAME = "twitter_tweets"
USER_TABLE_NAME = "twitter_users"
USER_META_TABLE_NAME = "twitter_user_meta"
FRIENDS_TABLE_NAME = "twitter_friends"
FOLLOWERS_TABLE_NAME = "twitter_followers"


class TweetsDB(BaseDB):
    def __init__(self, config = None):
        BaseDB.__init__(self, config=config)
        self.db = DBManager(config=config)
        self.session = self.db.session
        self.tweet_table = self.db.get_table(TWEETS_TABLE_NAME)
        self.user_table = self.db.get_table(USER_TABLE_NAME)
        self.user_meta_table = self.db.get_table(USER_META_TABLE_NAME)
        self.friends_table = self.db.get_table(FRIENDS_TABLE_NAME)
        self.followers_table = self.db.get_table(FOLLOWERS_TABLE_NAME)

        try:
            self.tweet_mapper = class_mapper(TweetObj)
        except UnmappedClassError:
            self.tweet_mapper = mapper(TweetObj,self.tweet_table)

        try:
            self.user_mapper = class_mapper(userObj)
        except UnmappedClassError:
            self.user_mapper = mapper(userObj,self.user_table)

        try:
            self.user_meta_mapper = class_mapper(userMetaObj)
        except UnmappedClassError:
            self.user_meta_mapper = mapper(userMetaObj,self.user_meta_table)

        try:
            self.friend_mapper = class_mapper(friendObj)
        except UnmappedClassError:
            self.friend_mapper = mapper(friendObj,self.friends_table)

        try:
            self.follower_mapper = class_mapper(followerObj)
        except UnmappedClassError:
            self.follower_mapper = mapper(followerObj,self.followers_table)

##
# New object creation routines
##

    ## Create "tweet" objects and records
    def new_tweet_table_item(self, rec=None):
        nto = TweetObj()
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
        uto = userObj()
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
        umto = userMetaObj()
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
        nf = friendObj()
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
        nf = followerObj()
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
        t = self.session.query(TweetObj).filter(TweetObj.tweet_id==tid).all()
        return t

    def query_tweet_table_by_username(self, uname=None, start_date=None, end_date=None):
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(TweetObj.from_user==uname)
        tlist = q.all()
        return tlist

    def query_tweet_table_by_user_id(self, uid=None, start_date=None, end_date=None):
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(TweetObj.from_user_id==uid)
        tlist = q.all()
        return tlist

    def query_tweet_table_by_tweet_substr(self, substr=None, start_date=None, end_date=None):
        qtext = "%"+substr+"%"
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        q = q.filter(TweetObj.tweet_text.like(qtext))
        tlist = q.all()
        return tlist

    def query_tweet_table_by_date_range(self, start_date=None, end_date=None, in_order=True):
        q = self._tweet_table_date_range(start_date=start_date, end_date=end_date)
        if( in_order ):
            q = q.order_by(TweetObj.created_at)
        tlist = q.all()
        return tlist

    def _tweet_table_date_range(self, start_date=None, end_date=None):
        query = self.session.query(TweetObj)
        if( start_date and end_date ):
            query = query.filter(TweetObj.created_at>=start_date, TweetObj.created_at<end_date)
        elif( start_date ):
            query = query.filter(TweetObj.created_at>=start_date)
        elif( end_date ):
            query = query.filter(TweetObj.created_at<end_date)
        else:
            pass
        return query

    ##
    ## Query the user table
    ##
    def query_user_table_by_fullname(self, sname):
        tlist = self.session.query(userObj).filter(userObj.screen_name==sname).all()
        return tlist

    def query_user_table_by_screenname(self, sname):
        tlist = self.session.query(userObj).filter(userObj.screen_name==sname).all()
        return tlist

    def query_user_table_by_username(self, uname):
        tlist = self.session.query(userObj).filter(userObj.user_name==uname).all()
        return tlist

    def query_user_table_by_user_id(self, uid):
        tlist = self.session.query(userObj).filter(userObj.user_id==uid).all()
        return tlist


    ##
    ## Query the user_meta table
    ##
    def query_user_meta_table_by_fullname(self, sname):
        tlist = self.session.query(userMetaObj).filter(userMetaObj.screen_name==sname).all()
        return tlist

    def query_user_meta_table_by_screenname(self, sname):
        tlist = self.session.query(userMetaObj).filter(userMetaObj.screen_name==sname).all()
        return tlist

    def query_user_meta_table_by_username(self, uname):
        tlist = self.session.query(userMetaObj).filter(userMetaObj.user_name==uname).all()
        return tlist

    def query_user_meta_table_by_user_id(self, uid):
        tlist = self.session.query(userMetaObj).filter(userMetaObj.user_id==uid).all()
        return tlist


    ##
    ## Query the friends table
    ##
    def query_friends_by_username(self, uname, fname=None):
        q = self.session.query(friendObj).filter(friendObj.user==uname)
        if( fname ):
            q = q.filter(friendObj.friend==fname)
        flist = q.all()
        return flist

    def query_friends_by_user_id(self, uid, fid=None):
        q = self.session.query(friendObj).filter(friendObj.user_id==uid)
        if( fid ):
            q = q.filter(friendObj.friend_id==fid)
        flist = q.all()
        return flist

    ##
    ## Query the followers table
    ##
    def query_followers_by_username(self, uname, fname=None):
        q = self.session.query(followerObj).filter(followerObj.user==uname)
        if( fname ):
            q = q.filter(followerObj.follower==fname)
        flist = q.all()
        return flist

    def query_followers_by_user_id(self, uid, fid=None):
        q = self.session.query(followerObj).filter(followerObj.user_id==uid)
        if( fid ):
            q = q.filter(followerObj.follower_id==fid)
        flist = q.all()
        return flist

