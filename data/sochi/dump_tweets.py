#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: dump_tweets.py
#   DATE: February, 2014
#   Author: David W. McDonald
#
#   Sample code that requests tweets from the DB and dumps each tweet
#   to the screen
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, gc, time, string, json, pickle, random
from datetime import datetime, timedelta
from infx.data.db.base.dbConfig import DBConfiguration
from infx.data.db.fitness.settings_db import *
from infx.data.db.fitness.FitTweetsDB import FitTweetsDB as DB
from infx.data.db.fitness.FitTweetObj import FitTweetObj
from infx.utils.tweet_entities import tweet_entities
from infx.utils.stop_words import remove_stops
from infx.data.fitness.constants import *

def query_date(db=None, date=None, dur=1, by_hour=False):
    result_list = []
    if( by_hour ):
        delta = timedelta(hours=1)
    else:
        delta = timedelta(days=1)
    dt2 = date + (dur*delta)
    start_date = date.strftime("%Y%m%d%H%M%S")
    end_date = dt2.strftime("%Y%m%d%H%M%S")
    #start_date = date.strftime("%Y%m%d000000")
    #end_date = dt2.strftime("%Y%m%d000000")
    try:
        result_list = db.query_tweet_table_by_date_range(start_date=start_date,
                                                         end_date=end_date,
                                                         in_order=True)
    except Exception, e:
        print "EXCEPTION when running query!"
        print e
        result_list = []
    return {'tweet_list':result_list, 
            'query_date':date, 
            'start_date_str':start_date, 
            'end_date_str':end_date,
            'duration':dur}


def tweet_dump(db=None, start_date=None, dur=1, items=-1, obj=False, report=False):
    
    # query the database to get a set (list) of tweets
    result = query_date(db=db, date=start_date, dur=dur)
    tweet_list = result['tweet_list']
    
    total_tweets = 0
    if( report ):
        total_tweets = len(tweet_list)
        print "Found %d tweets."%(total_tweets)
    
    if( items>0 ):
        tweet_list = tweet_list[:items]
    
    # now iterate through the list of the tweet objects
    counter = 0
    for tweet in tweet_list:
        counter+=1
        print "Tweet [%6d]:"%counter
        if( obj ):
            # this version uses the __repr__ version of the object
            # this is very similar to the version below
            print tweet
        else:
            # this version just picks out a few specific items from the
            # object and prints them
            print "Tweet Type %s:"%(type(tweet))
            print "tweet_id(%s):"%(type(tweet.tweet_id)),tweet.tweet_id
            print "tweet_id_str(%s):"%(type(tweet.tweet_id_str)),tweet.tweet_id_str
            print "created_at(%s):"%(type(tweet.created_at)),tweet.created_at
            print "query_source(%s):"%(type(tweet.query_source)),tweet.query_source
            print "from_user(%s):"%(type(tweet.from_user)),tweet.from_user.encode('utf-8')
            print "from_user_name(%s):"%(type(tweet.from_user_name)),tweet.from_user_name.encode('utf-8')
            print "from_user_id(%s):"%(type(tweet.from_user_id)),tweet.from_user_id
            ttext = tweet.tweet_text.replace("\n","").replace("\r","")
            print "tweet_text(%s)"%(type(tweet.tweet_text)),ttext.encode('utf-8')
        print
        
    if( report ):
        print "Found %d tweets."%(total_tweets)
        print "Dumped %d tweets."%(counter)
    return


def parse_date(dstr=None):
    date = None
    try:
        date = datetime.strptime(dstr,"%Y%m%d")
    except:
        try:
            date = datetime.strptime(dstr,"%d-%m-%Y")
        except:
            try:
                date = datetime.strptime(dstr,"%d/%m/%Y")
            except:
                print "Can't parse that date."
                date = None
    return date


def parse_params(argv):
    dt = None          # date for the doc
    dt_str = None      # date as a string entered by the user
    dur = 1            # duration
    items = 0          # number of items to include
    objects = False    # just dump the tweet objects
    report = True      # report progress
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-date"):
            pc += 1
            dt_str = argv[pc]
            dt = parse_date(dt_str)
        if( param == "-dur"):
            pc += 1
            dur = int(argv[pc])
        if( param == "-items"):
            pc += 1
            items = int(argv[pc])
        if( param == "-obj"):
            objects = True
        if( param == "-report"):
            report = True
        if( param == "-no_report"):
            report = False
        pc += 1
    return {'date':dt, 'dt_str':dt_str,
            'report':report, 'items':items,
            'objects':objects, 'duration':dur }


def usage(prog):
    print "USAGE: %s -date <date> [-dur <days>] [-items <n_items>] [-obj] [-report | -no_report]"%(prog)
    sys.exit(0)


# Some simple examples of using this at the command line
#
#   python dump_tweets.py -date 20130101
#   python dump_tweets.py -date 20130101 -items 10
#   python dump_tweets.py -date 20130101 -items 10 -obj

def main(argv):
    if len(argv) < 3:
        usage(sys.argv[0])
    params = parse_params(argv)

    if( params['report'] ):
        print "Got parameters"
        print params

    if( params['report'] ):
        print "Preparing Database Configuration"
    config = DBConfiguration(db_settings=DATABASE_SETTINGS['default'])
    #config = DBConfiguration(db_settings=DATABASE_SETTINGS['main_db'])

    if( params['report'] ):
        print config
        print "Opening Database"
    
    # Open the database with the specific configuration
    db = DB(config=config)
        
    doc = tweet_dump(db=db,start_date=params['date'],
                           dur=params['duration'],
                           items=params['items'],
                           obj=params['objects'],
                           report=params['report'])

    
    # Always remember to close the DB when you're done
    db.close()
    return


if __name__ == '__main__':
    main(sys.argv)
