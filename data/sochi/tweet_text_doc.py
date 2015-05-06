#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: tweet_text_doc.py
#   DATE: December, 2013
#   Author: David W. McDonald
#
#   Create a text document from a set of collected tweets
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


def tweet_doc(db=None, start_date=None, dur=1, lines=-1, stops=False, as_list=False, report=False):
    doc_list = []
    doc = u""
    
    # query the database to get a set (list) of tweets
    result = query_date(db=db, date=start_date, dur=dur)
    tweet_list = result['tweet_list']
    
    if( report ):
        print "Found %d tweets."%(len(tweet_list))
    
    # now iterate through the list of the tweet objects
    for tweet in tweet_list:
        # remove any newline or carriage return in each tweet
        fixed_tweet = tweet.tweet_text.replace("\n"," ").replace("\r"," ")
        # if we're supposed to remove stop words, then remove them
        if( stops ):
            fixed_tweet = remove_stops(fixed_tweet)
        # now add the tweet to the list
        doc_list.append(fixed_tweet)
    
    # if we're keeping only a few of the lines, cut the list down
    if( lines>0 ):
        doc_list = doc_list[0:lines]
    
    if( as_list ):
        # just keep it as a list of individual tweets
        doc = doc_list
    else:
        # now join the list as a single document
        doc = u"\n".join(doc_list)
        
    if( report ):
        print "Tweet Doc length:",len(doc)
        print doc
        print "Tweet Doc length:",len(doc)
    return doc


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
    stops = False      # remove stop words when processing
    pickle = False     # pickle the result
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
        if( param == "-stops"):
            stops = True
        if( param == "-pickle"):
            pickle = True
        if( param == "-report"):
            report = True
        if( param == "-no_report"):
            report = False
        pc += 1
    return {'date':dt, 'dt_str':dt_str, 'report':report, 'items':items,
            'stops':stops, 'pickle':pickle, 'duration':dur }


def usage(prog):
    print "USAGE: %s -date <date> [-dur <days>] [-items <n_items>] [-stops] [-pickle] [-report | -no_report]"%(prog)
    sys.exit(0)


# Some simple examples of using this at the command line
#
#   python tweet_text_doc.py -date 20130101
#   python tweet_text_doc.py -date 20130101 -items 10
#   python tweet_text_doc.py -date 20130101 -items 10 -stops
#   python tweet_text_doc.py -date 20130201 -dur 2 -pickle
#   python tweet_text_doc.py -date 20130301 -pickle -no_report

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
    
    # Open the database witht he specific configuration
    db = DB(config=config)
        
    doc = tweet_doc(db=db,start_date=params['date'],
                          dur=params['duration'],
                          lines=params['items'],
                          stops=params['stops'],
                          report=params['report'])

    # Pickle the result as a dictionary with a key as the date in YYYYMMDD format
    # note that for any given date the duration is not kept as part of the key
    # but that the duration is part of the file name
    if( params['pickle'] ):
        dt_str = params['date'].strftime("%Y%m%d")
        fname = "tweet_doc-"+dt_str+"-dur%02d"%(params['duration'])+".pickle"
        pf = open(fname,"w")
        doc_dict = {dt_str:doc}
        pickle.dump(doc_dict,pf)
        pf.close()
    
    # Always remember to close the DB when you're done
    db.close()
    return


if __name__ == '__main__':
    main(sys.argv)
