#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: UserTimeline.py
#
#   An example object relying on the Twitter REST API to collect a set
#   of tweets posted by the specified user. Currently, twitter restricts
#   this to 200 tweets per request. Use the since_id and max_id to cursor
#   forward or backward through the users list of tweets.
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, logging
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class UserTimeline(TwitterBase):
    def __init__(self, 
                 name="UserTimeline",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                              args=args, kwargs=kwargs)
        self.usertimeline_url ="https://api.twitter.com/1.1/statuses/user_timeline.json"
        self.max_statuses = 200
        self.set_request_type_as_usertimeline()

    ##
    # Sets the domain to the general search interface
    #
    def set_request_type_as_usertimeline(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_request_domain(self.usertimeline_url)
            self.set_rate_limit_resource("statuses","user_timeline")

    ##
    # Set the user name of the statuses that will be requested
    #
    def set_username(self, username=None):
        if( not self.querying ):
            # if setting the username, then unset the user_id
            self.set_request_param(kw="screen_name",val=username)
            self.set_request_param(kw="user_id",val=None)
            #self._set_cursor()

    ##
    # Set the user ID of the statuses that will be requested
    #
    def set_user_id(self, uid=None):
        if( not self.querying ):
            # if setting the user_id, then unset the screen_name
            self.set_request_param(kw="user_id",val=str(uid))
            self.set_request_param(kw="screen_name",val=None)
            #self._set_cursor()

    ##
    # Set the number of status items to be returned
    #
    def set_count(self, c=None):
        if( not self.querying ):
            if( c ):
                if( int(c) < 0 ):
                    self.set_request_param(kw="count",val=None)
                elif( int(c) > self.max_statuses ):
                    self.set_request_param(kw="count",val=str(self.max_statuses))
                else:
                    self.set_request_param(kw="count",val=str(c))
            else:
                self.set_request_param(kw="count",val=None)
    
    ##
    # When this parameter is set the result removes any retweets
    #
    def set_include_rts(self,rts=True):
        if( not self.querying ):
            if( rts ):
                self.set_request_param(kw="include_rts",val="true")
            else:
                self.set_request_param(kw="include_rts",val=None)

    ##
    # This parameter sets the query to return a trimmed (very short)
    # versio of the user record.
    #
    def set_trim_user(self,trim=True):
        if( not self.querying ):
            if( trim ):
                self.set_request_param(kw="trim_user",val="true")
            else:
                self.set_request_param(kw="trim_user",val=None)

    ##
    # Sets the request to return tweets with IDs greater than the
    # given tweet ID (that is, "newer" tweets)
    #
    def set_since_id(self,sid=None):
        if( not self.querying ):
            if( sid ):
                self.set_request_param(kw="since_id",val=str(sid))
            else:
                self.set_request_param(kw="since_id",val=None)

    ##
    # Sets request to return tweets with IDs less than the given
    # tweet ID (generally, these are "older" tweets)
    #
    def set_max_id(self,mid=None):
        if( not self.querying ):
            if( mid ):
                self.set_request_param(kw="max_id",val=str(mid))
            else:
                self.set_request_param(kw="max_id",val=None)

    ##
    # Sets the request to exclued replies by this user to another user
    #
    def set_exclude_replies(self,repl=None):
        if( not self.querying ):
            if( repl ):
                self.set_request_param(kw="exclude_replies",val=str(repl))
            else:
                self.set_request_param(kw="exclude_replies",val=None)

    ##
    # 
    #
    def make_request(self):
        # this code is not reentrant, don't make the request twice
        if( self.querying ):
            return

        self.querying = True
        self.warning_or_error = False
        self.last_warning_message = {}
        
        # user timelines do not support continuation, must use since ID or
        # max ID as indexing methods
        try:
            self.set_request(domain=self.get_request_domain(),
                            method="GET",
                            params=self.get_request_params())
            if( self.debug_output ):
                print "REGULAR REQUEST:"
                print json.dumps(self._request_data, sort_keys=True, indent=4)

            request_results = self._make_request(request=self._request_data)
            js = None
            if( request_results or request_results.text ):
                try:
                    js = request_results.json()
                except ValueError, e:
                    mesg = "JSON ValueError: "+str(e)
                    self.logger.info(mesg)
                    js = None
                
            # this should come back as just a list of tweets
            if( js and (type(js) == list) ):
                #print "IN make_request()"
                #print json.dumps(js, sort_keys=True, indent=4)
                # don't bother to add this if it's an empty list
                if( len(js) > 0 ):
                    self.put_message(m=js)
                    rinfo = self.get_request_info()
                    if( rinfo ):
                        rinfo['success']=True

            self.querying = False
        except:
            self.querying = False
            raise
        return

def parse_params(argv):
    uid = None
    username = None
    count = 200
    auth = None
    user = None
    since = None
    maxid = None
    continuation = False
    json = False
    logging = False
    debug = False
    limits = False
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]

        if( param == "-n"):
            pc += 1
            username = argv[pc]
        if( param == "-name"):
            pc += 1
            username = argv[pc]
        if( param == "-uname"):
            pc += 1
            username = argv[pc]
        if( param == "-id"):
            pc += 1
            uid = argv[pc]
        if( param == "-count"):
            pc += 1
            count = int(argv[pc])
        if( param == "-c"):
            pc += 1
            count = int(argv[pc])
        if( param == "-since"):
            pc += 1
            since = argv[pc]
        if( param == "-s"):
            pc += 1
            since = argv[pc]
        if( param == "-max"):
            pc += 1
            maxid = argv[pc]
        if( param == "-m"):
            pc += 1
            maxid = argv[pc]

        if( param == "-log"):
            logging = True
        if( param == "-debug"):
            debug = True
        if( param == "-json"):
            json = True
        if( param == "-limits"):
            limits = True
        pc += 1
    return {'auth':auth, 'user':user,
            'uname':username, 'count':count, 'uid':uid,
            'since':since, 'max_id':maxid, 
            'limits':limits, 'json':json,  
            'logging':logging, 'debug':debug }


def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> [-n <username> | -id <userid>] [-c <count>] [-s <since_id>] [-m <max_id>] [-log]"%(argv[0])
    sys.exit(0)

def main(argv):
    if len(argv) < 2:
        usage(argv)

    p = parse_params(argv)
    print p

    twit = UserTimeline()
    twit.set_user_agent(agent="random")
    twit.set_throttling(True)

    if( p['debug'] ):
        twit.debug_output = True

    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="UserTimelineLogin",
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
    
    if( p['uname'] ):
        print "Requesting user:",p['uname']
        twit.set_username(p['uname'])
        user = p['uname']
    elif( p['uid'] ):
        print "Requesting UID:",p['uid']
        twit.set_user_id(long(p['uid']))
        user = p['uid']
    else:
        twit.set_username("BronxZoosCobra")
        user = "BronxZoosCobra"

    twit.set_count(p['count'])
    
    if( p['since'] ):
        twit.set_since_id(p['since'])
    if( p['max_id'] ):
        twit.set_max_id(p['max_id'])
    
    twit.start_thread()
    twit.start_request()
    
    # The request is being made by an asynchronous thread, we need
    # to wait until that thread is done before we can see the result.
    #
    # This convenience routine must be called by a different thread.
    # In our case here, we're in the "__main__" thread which can make
    # this call and safely wait until the twit thread is done.
    twit.wait_request()

    if( twit.messages()==0 ):
        print "No results from query."
        return

    m = None
    while( twit.messages()>0 or twit.query_in_process() ):
        if( twit.messages()==0 ):
            time.sleep(2)
        m = twit.get_message()
        if( m ):
            #print json.dumps(m, indent=4, sort_keys=True)
            if( type(m)==dict ):
                if( ("errors" in m) or ("error" in m) ):
                    try:
                        error = m['errors'][0]
                    except:
                        error = m['error']
                    print "\tError %d: %s"%(error['code'],error['message'])
                else:
                    print "Not sure about this response:"
                    print json.dumps(m, indent=4, sort_keys=True)
            else:
                count = 0
                for tweet in m:
                    count += 1
                    if( p['json'] ):
                        print json.dumps(tweet, sort_keys=True, indent=4)
                    else:
                        print "%4d: %s (%s):"%(count,user,tweet['user']['id_str']),
                        print tweet['text'].encode('utf-8')
                        print "%25s, %s"%(tweet['id_str'],tweet['created_at'])
                print "Have %d total tweets!"%count

    if( p['limits'] ):
        print "Limits:",twit.get_rate_limit(),twit._throttling()

    twit.terminate_thread()
    return

if __name__ == '__main__':
    main(sys.argv)
