#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: collect_tweets.py
#   DATE: January, 2014
#   Author: David W. McDonald
#
#   A simple tweet collector for INFX 547
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, json, time, re
from datetime import datetime
from sochi.data.db.base.dbConfig import DBConfiguration
from sochi.data.db.sochi.ExampleTweetObj import ExampleTweetObj
from sochi.data.db.sochi.ExampleTweetsDB import ExampleTweetsDB
from sochi.data.db.sochi.settings_db import *
from sochi.twitter.Login import Login
from sochi.twitter.Search import Search
from sochi.twitter.auth_settings import *

#nasty_unicode = u'Some example text with a sleepy face \U0001f62a and fist \U0001f44a bah!'

# This is a regular expression that matches all 
# characters which are NOT 1, 2, or 3 bytes long
# Actually, this should probably be called "MySQL_utf8_acceptable"
#
utf8_acceptable = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)

def dump_tweet(rec=None, mesg_count=None, tweet_count=None):
    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count),
    print rec['user']['screen_name'].encode('utf-8'),rec['user']['name'].encode('utf-8'),
    print ":",rec['text'].encode('utf-8')
    print

def dump_json(rec=None, mesg_count=None, tweet_count=None):
    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count)
    print json.dumps(rec, sort_keys=True, indent=4)
    print

def collection_loop(db=None, twit=None, term=None):
    tweet_count = 0
    mesg_count = 0
    total_tweets = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        message_list = twit.get_message()
        mesg_count += 1
        if( message_list ):
            total_tweets = total_tweets + len(message_list)
            #print json.dumps(message_list, sort_keys=True, indent=4)
            for tweet in message_list:
                tweet_count += 1
                #dump_json(rec=tweet,mesg_count=mesg_count,tweet_count=tweet_count)
                dump_tweet(rec=tweet,mesg_count=mesg_count,tweet_count=tweet_count)
                source = "command_line:%s"%(str(term))
                save_tweet(db=db, tweet=tweet, source=source)
                save_user(db=db, tweet=tweet)
        while( twit.messages()<1 and twit.query_in_process() ):
            time.sleep(2)
    db.commit_changes()
    return

def save_user(db=None, tweet=None):
    if( tweet and (type(tweet) is dict) ):
        uname = tweet['user']['screen_name'].encode('utf-8')
        ulist = db.query_user_table_by_username(uname)
        if( len(ulist) > 0 ):
            print "\tAlready have this user:",tweet['user']['screen_name'].encode('utf-8'),
            print "[%s]"%(tweet['user']['id_str'])
            return
        rec = db.new_user_table_item(None)
        username = tweet['user']['screen_name'].encode('utf-8')
        rec.user_name = username
        rec.screen_name = tweet['user']['name'].encode('utf-8')
        rec.user_id = long(tweet['user']['id_str'])
        db.insert_item(rec)
    return


def save_tweet(db=None, tweet=None, source=""):
    if( tweet and (type(tweet) is dict) ):
        rlist = db.query_tweet_table_by_tweet_id(str(tweet['id']))
        if( len(rlist) > 0 ):
            print "\tAlready have this tweet:",tweet['id'],
            print "%s"%(str(tweet['created_at']))
            return
        rec = db.new_tweet_table_item(None)
        rec.tweet_id = tweet['id']
        rec.tweet_id_str = tweet['id_str']
        #print tweet['created_at']
        ## changed date format
        ts = tweet['created_at'].rpartition(' ')[0]
        yr = tweet['created_at'].rpartition(' ')[2]
        ts = ts.rpartition(' ')[0]
        dstr = ts+" "+yr
        #print tweet['created_at']," ALT:",ts
        #created_dt = datetime.strptime(ts,"%a, %d %b %Y %H:%M:%S")
        created_dt = datetime.strptime(dstr,"%a %b %d %H:%M:%S %Y")
        rec.created_at = created_dt
        ## new user structure/format
        rec.from_user_name = tweet['user']['name'].encode('utf-8')
        rec.from_user = tweet['user']['screen_name'].encode('utf-8')
        rec.from_user_id = long(tweet['user']['id_str'])
        
        # This does not work with 4byte utf-8 strings
        # Actually this is not a Python problem it is a MySQL issue
        #rec.tweet_text = tweet['text'].encode('utf-8')

        # We use a regular expression to clean the tweet of any characters
        # that would generate a 4 byte utf-8 encoding. Note another fix would
        # be to install a MySQL version higher than 5.5 and make the table 
        # be utf8mb4 compatible, then make python encode everything as utf8mb4
        strict_utf8_tweet = utf8_acceptable.sub(u'',tweet['text'])        
        rec.tweet_text = strict_utf8_tweet
        
        rec.query_source = source
        if( tweet['geo'] ):
            # {u'type': u'Point', u'coordinates': [33.512999999999998, 36.292000000000002]}
            geo = tweet['geo']
            if( (geo['type']=="Point") or (geo['type']=="point") ):
                coord = geo['coordinates']
                rec.lat = coord[0]
                rec.lon = coord[1]
            else:
                print "\tUnexpected Geo type: ",str(geo)
        db.insert_item(rec)
    else:
        print "NOT a tweet dictionary:",type(tweet)
    return


def parse_params(argv):
    auth = None
    user = None
    query = None
    size = 100

    continuation = False
    debug = False
    json = False
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]
        if( param == "-query"):
            pc += 1
            query = argv[pc]
        if( param == "-page_size"):
            pc += 1
            size = int(argv[pc])
        
        if( param == "-cont"):
            continuation = True
        if( param == "-debug"):
            debug = True
        if( param == "-json"):
            json = True
        pc += 1

    return {'auth':auth, 'user':user,
            'query':query, 'json':json, 'page_size':size,
            'use_continuations':continuation, 'debug':debug }

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> -query \"<query_terms>\" [-page_size <n>] [-cont] [-debug] [-json]"%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 5:
        usage(argv)
    p = parse_params(argv)
    print p
    
    twit = Search()
    twit.set_user_agent(agent="random")
    twit.set_throttling(True)

    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="SampleTweetCollectorLoginObj",
                    app_name=p['auth'],
                    app_user=p['user'],
                    token_fname=app_token_fname)
        if( p['debug'] ):
            lg.set_debug(True)
        ## Key and secret for specified application
        lg.set_consumer_key(consumer_key=app_keys['consumer_key'])
        lg.set_consumer_secret(consumer_secret=app_keys['consumer_secret'])
        lg.login()
        twit.set_auth_obj(obj=lg)

    if( not p['query'] ):
        print "Must provide some query terms!"
        usage(argv)

    if( p['use_continuations'] ):
        print "Using Continuations for requests"
        twit.set_continuation(True)

    print "Collecting tweets for term:", p['query'].encode('utf-8')
    twit.set_query_terms(p['query'].encode('utf-8'))
    twit.set_query_result_type(rt="recent")
    twit.set_page_size(sz=p['page_size'])
    #twit.set_page_size(sz=5)

    db_config = DBConfiguration(db_settings=DATABASE_SETTINGS['main_db'])
    db = ExampleTweetsDB(config=db_config)

    twit.start_thread()
    twit.start_request()
    twit.wait_request()

    collection_loop(db=db,twit=twit)

    return


if __name__ == '__main__':
    main(sys.argv)
