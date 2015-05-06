#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: simple_sample.py
#   DATE: December, 2013
#   Author: David W. McDonald
#
#   Sample tweets from the health and fitness dataset
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, gc, time, string, json, csv, random, json, pickle, cPickle
from datetime import datetime, timedelta
from sochi.data.db.base.dbConfig import DBConfiguration
from sochi.data.db.sochi.settings_db import *
from sochi.data.db.sochi.ExampleTweetsDB import ExampleTweetsDB as DB
from sochi.data.db.sochi.ExampleTweetObj import ExampleTweetObj
from sochi.utils.tweet_entities import tweet_entities
from sochi.data.sochi.constants import *
import csv





def str_to_datetime(date_str=None):
    dt = None
    try:
        dt = datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")
    except:
        try:
            dt = datetime.strptime(date_str,"%Y %m %d")
        except:
            dt = None
    return dt

def next_day(dt=None, dt_str=None):
    if( dt ):
        start_dt = dt
    else:
        start_dt = str_to_datetime(dt_str)
    delta_day = timedelta(days=1)
    new_dt = start_dt + delta_day
    new_dt_str = new_dt.strftime("%Y-%m-%d %H:%M:%S")
    return {'dt':new_dt, 'dt_str':new_dt_str}

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


def sample_tweets(tweet_list=None, samples=None, day=None, report=False):
    result_list = []
    f = open("record.csv", "a")
    if( len(tweet_list)<=samples ):
        result_list=tweet_list
        if( report ):
            print "\tFewer tweets this day than samples, returning all!"
    else:
        count = 0
        while( count < samples):
            random_index = random.randint(0,(len(tweet_list)-1))
            tweet = tweet_list[random_index]
            #tweetwriter = csv.DictWriter(f, delimiter=',')
            f.write(tweet.tweet_text.encode('utf-8'))
            f.write("\n")
            #tweetwriter.writerows(tweet.tweet_text.encode('utf-8'))
            if( report ):
                print "\t[%d:%d]>>"%(day,count),
                print tweet.tweet_text.encode('utf-8')
                #print tweet
            result_list.append(tweet)
            del tweet_list[random_index]
            count += 1
    f.flush()
    f.close()
    return result_list


def process_week(db=None, week=0, p=None, report=True):
    week_samples = []
    if( (week>=MIN_WEEK_INDEX) and (week<=MAX_WEEK_INDEX) ):
        if( report ):
            print "Starting Week: %d"%week
        current_dt = str_to_datetime(WEEKS[str(week)][0])
        end_dt = str_to_datetime(WEEKS[str(week)][1])
        tweet_count = 0
        day = 1
        while( current_dt < end_dt ):
            sample_list = []
            if( report ):
                print "Processing Day:",str(current_dt)
            result = query_date(db=db,date=current_dt,dur=1)
            tweet_list = result['tweet_list']
            if( report ):
                print "\tTweets this day:",len(tweet_list)
            sample_list = sample_tweets(tweet_list=tweet_list, samples=p['samples'],
                                        day=day, report=report)
            next_dt_rec = next_day(dt=current_dt)
            current_dt = next_dt_rec['dt']
            sys.stdout.flush()
            sys.stderr.flush()
            gc.collect()
            time.sleep(3.0)
            day += 1
            week_samples.extend(sample_list)
        if( report ):
            print "Finished Week: %d"%(week)
    return week_samples


def process_weeks(db=None, p=None):
    for week in range(p['week'][0],(p['week'][1]+1)):
        if( (week>=MIN_WEEK_INDEX) and (week<=MAX_WEEK_INDEX) ):
            if( p['report'] ):
                print "Week:",week
            total_samples = process_week(db=db,week=week,p=p,report=p['report'])
            if( p['report'] ):
                print "Total Samples:",len(total_samples)
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


def parse_range(r=None):
    start = 0
    end = 0
    start_str = r.partition('-')[0]
    end_str = r.partition('-')[2]
    if( start_str ):
        start = int(start_str)
        end = start
    if( end_str ):
        end = int(end_str)
    return [start,end]


def parse_params(argv):
    week = [1,1]       # just process the first week
    all = False        # process all weeks with data
    report = True      # report progress
    samples = 30        # the number of samples per week in each class
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-week"):
            pc += 1
            week = parse_range(argv[pc])
        if( param == "-all"):
            week = [1,13]

        if( param == "-samples"):
            pc += 1
            samples = int(argv[pc])
        if( param == "-s"):
            pc += 1
            samples = int(argv[pc])
        
        if( param == "-report"):
            report = True
        if( param == "-no_report"):
            report = False
        pc += 1
    return {'week':week, 'report':report, 'samples':samples }


def usage(prog):
    print "USAGE: %s [-week <n>-<m>] [-all] [-samples <n, per day>] [-report | -no_report]"%(prog)
    sys.exit(0)


def main(argv):
    if len(argv) < 2:
        usage(sys.argv[0])
    params = parse_params(argv)

    if( params['report'] ):
        print "Got parameters"
        print params

    if( params['report'] ):
        print "Preparing Database Configuration"
    config = DBConfiguration(db_settings=DATABASE_SETTINGS['main_db'])
    #config = DBConfiguration(db_settings=DATABASE_SETTINGS['default'])

    if( params['report'] ):
        print config
        print "Opening Database"
    
    # Open the database with he specific configuration
    db = DB(config=config)
        
    process_weeks(db=db,p=params)
    
    # Always remember to close the DB when you're done
    db.close()
    return


if __name__ == '__main__':
    main(sys.argv)
