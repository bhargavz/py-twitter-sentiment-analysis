#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: find_hashtags.py
#   DATE: Feb 2014
#   Author: Bhargav Shah
#
#   Example of processing tweets to find hashtag use and frequency
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, gc, time, string, json, pickle, random
from datetime import datetime, timedelta
from sochi.data.db.base.dbConfig import DBConfiguration
from sochi.data.db.sochi.settings_db import *
from sochi.data.db.sochi.ExampleTweetsDB import ExampleTweetsDB as DB
from sochi.data.db.sochi.ExampleTweetObj import ExampleTweetObj
from sochi.utils.tweet_entities import tweet_entities
from sochi.data.fitness.constants import *

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


def find_hashtags(db=None, start_date=None, dur=1, report=False):
    hashtag_dict = {}
    
    # query the database to get a set (list) of tweets
    result = query_date(db=db, date=start_date, dur=dur)
    tweet_list = result['tweet_list']
    
    if( report ):
        print "Found %d tweets."%(len(tweet_list))
    
    # now iterate through the list of the tweet objects
    for tweet in tweet_list:
        tweet_stuff = tweet_entities(tweet_text=tweet.tweet_text)
        tweet_hashes = tweet_stuff['hashes']
        #if( report and tweet_hashes ):
        #    print tweet_hashes
        for hashtag in tweet_hashes:
            if( hashtag in hashtag_dict ):
                hash_list = hashtag_dict[hashtag]
                hash_list.append( tweet )
            else:
                hashtag_dict[hashtag] = [tweet]
        
    if( report ):
        print "Found %d unique hashtags"%(len(hashtag_dict))
        
    return hashtag_dict


def order_hashtags(hashtag_dict=None):
    counted_ht = {}
    
    for ht in hashtag_dict:
        counted_ht[ht] = len(hashtag_dict[ht])
    
    ordered_tags = sorted(counted_ht.items(), key=lambda x: x[1], reverse=True)
    return ordered_tags


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
    report = True      # report progress
    pickle = False     # pickle the result
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
        if( param == "-pickle"):
            pickle = True
        if( param == "-report"):
            report = True
        if( param == "-no_report"):
            report = False
        pc += 1
    return {'date':dt, 'dt_str':dt_str, 'report':report, 'pickle':pickle, 'duration':dur }


def usage(prog):
    print "USAGE: %s -date <date> [-dur <days>] [-pickle] [-report | -no_report]"%(prog)
    sys.exit(0)


# Some simple examples of using this at the command line
#
#   python find_hashtags.py -date 20130101
#   python find_hashtags.py -date 20130201 -dur 2 -pickle
#   python find_hashtags.py -date 20130301 -pickle -no_report

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
        
    htd = find_hashtags(db=db,start_date=params['date'],
                          dur=params['duration'],
                          report=params['report'])

    if( params['report'] ):
        ranked = order_hashtags(hashtag_dict=htd)
        for item in ranked:
            #print "%5d: %s"%(item[1],item[0])
            print "%5d:"%(item[1]),item[0].encode('utf-8')

    # Pickle the resulting hashtag dictionary
    if( params['pickle'] ):
        dt_str = params['date'].strftime("%Y%m%d")
        fname = "hashtag_dict-"+dt_str+"-dur%02d"%(params['duration'])+".pickle"
        pf = open(fname,"w")
        pickle.dump(htd,pf)
        pf.close()
    
    # Always remember to close the DB when you're done
    db.close()
    return


if __name__ == '__main__':
    main(sys.argv)
