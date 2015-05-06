#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: FriendsFollowers.py 
#
#   Object to request friends and followers of the specified user. This request
#   requires cursoring. This really requires throttling because of the number of
#   friends/followers are very large. Therefore, throttling this on by default.
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, logging
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class FriendsFollowers(TwitterBase):
    def __init__(self, 
                 name="FriendsFollowers",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                              args=args, kwargs=kwargs)
        self.friends_url = "https://api.twitter.com/1.1/friends/ids.json"
        self.followers_url = "https://api.twitter.com/1.1/followers/ids.json"
        self.cursor_forward = True
        self.next_cursor = None
        self.prev_cursor = None
        self.set_request_type_as_friends()
        

    ##
    # Sets the domain to the friend search
    #
    def set_request_type_as_friends(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_request_domain(self.friends_url)
            self.set_rate_limit_resource("friends","ids")
            self._set_cursor()
            # should *almost always* throttle these friends/followers queries
            self.set_throttling(tr=True)

    ##
    # Sets the domain to the friend search
    #
    def set_request_type_as_followers(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_request_domain(self.followers_url)
            self.set_rate_limit_resource("followers","ids")
            self._set_cursor()
            # should *almost always* throttle these friends/followers queries
            self.set_throttling(tr=True)

    ##
    # Set the user (username/screen name) whose friends/followers will
    # be returned
    #
    def set_username(self, un=None):
        if( not self.querying ):
            # if setting the username, then unset the user_id
            self.set_request_param(kw="screen_name",val=un)
            self.set_request_param(kw="user_id",val=None)
            self._set_cursor()

    ##
    # Set the user (username/screen name) whose friends/followers will
    # be returned
    #
    def set_screen_name(self, sc=None):
        self.set_username(un=sc)

    ##
    # Set the user (user_id) whose friends/followers will be returned
    #
    def set_user_id(self, uid=None):
        if( not self.querying ):
            # if setting the user_id, then unset the screen_name
            self.set_request_param(kw="user_id",val=str(uid))
            self.set_request_param(kw="screen_name",val=None)
            self._set_cursor()

    ##
    # Set the count, the number of ids to be returned, current default
    # for twitter is 5000 ids per request
    #
    def set_count(self, c=5000):
        if( not self.querying ):
            self.set_request_param(kw="count",val=str(c))

    ##
    # Sets the cursor for the current request
    #
    def _set_cursor(self, cursor="-1"):
        if( cursor ):
            self.set_request_param(kw="cursor",val=str(cursor))
        else:
            self.set_request_param(kw="cursor",val=None)

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
        try:
            self.next_cursor = -1
            self.prev_cursor = -1
            if( self.cursor_forward ):
                self._set_cursor(cursor=self.next_cursor)
                cursor_end = self.next_cursor
            else:
                self._set_cursor(cursor=self.prev_cursor)
                cursor_end = self.prev_cursor
            
            while( cursor_end ):
                self.set_request(domain=self.get_request_domain(),
                                    method="GET",
                                    params=self.get_request_params())
                request_results = self._make_request(request=self._request_data)
                if( request_results or request_results.text ):
                    try:
                        js = request_results.json()
                        #print "IN make_request() cursor=%d"%(next_cursor)
                        #print json.dumps(js, sort_keys=True, indent=4)
                        self.put_message(m=js)
                        if( "error" in js ):
                            self.next_cursor = 0
                            self.prev_cursor = 0
                        else:
                            if( "next_cursor" in js ):
                                self.next_cursor = js['next_cursor']
                            else:
                                self.next_cursor = 0
                            if( "previous_cursor" in js ):
                                self.prev_cursor = js['previous_cursor']
                            else:
                                self.prev_cursor = 0
                        
                        if( self.cursor_forward ):
                            self._set_cursor(cursor=self.next_cursor)
                            cursor_end = self.next_cursor
                        else:
                            self._set_cursor(cursor=self.prev_cursor)
                            cursor_end = self.prev_cursor
                    except ValueError, e:
                        mesg = "JSON ValueError: "+str(e)
                        self.logger.info(mesg)
                        js = None
                        cursor_end = 0
                else:
                    cursor_end = 0
            self.querying = False
        except:
            self.querying = False
            raise
        return

def parse_params(argv):
    auth = None
    user = None
    uname = None
    uid = None
    count = 0
    followers = True
    logging = False
    json = False
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
            uname = argv[pc]
        if( param == "-name"):
            pc += 1
            uname = argv[pc]
        if( param == "-id"):
            pc += 1
            uid = argv[pc]
        if( param == "-uid"):
            pc += 1
            uid = argv[pc]
        if( param == "-count"):
            pc += 1
            count = int(argv[pc])
        
        if( param == "-friends"):
            followers = False
        if( param == "-followers"):
            followers = True
        
        if( param == "-log"):
            logging = True
        if( param == "-json"):
            json = True
        if( param == "-limits"):
            limits = True
        pc += 1
    return {'auth':auth, 'user':user,
            'followers':followers, 'uid':uid, 'uname':uname, 'count':count,
            'logging':logging, 'json':json, 'limits':limits }

#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -friends -name aplusk
#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -friends -name apluskTV
#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -friends -name NatGeo
#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -friends -name timoreilly

#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -followers -name dwmcphd -count 5
#python FriendsFollowers.py -auth INFX547Test01 -user infxtweets -followers -name timoreilly

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> [-friends | -followers] -n <username> | -id <userid> [-count <count_per_request>] [-json]"%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 6:
        usage(argv)
    p = parse_params(argv)
    print p

    twit = FriendsFollowers()
    twit.set_user_agent(agent="random")
    twit.set_throttling(True)

    if( p['logging'] ):
        log_fname = twit.get_preferred_logname()
        fmt='[%(asctime)s][%(module)s:%(funcName)s():%(lineno)d] %(levelname)s:%(message)s'
        logging.basicConfig(filename=log_fname,format=fmt,level=logging.INFO)
        log = logging.getLogger("twit_tools")

    if( p['followers'] ):
        print "Requesting FOLLOWERS"
        twit.set_request_type_as_followers()
    else:
        print "Requesting FRIENDS"
        twit.set_request_type_as_friends()

    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="FriendsFollowersLoginObj",
                    app_name=p['auth'],
                    app_user=p['user'],
                    token_fname=app_token_fname)
        #lg.set_debug(True)
        ## Key and secret for specified application
        lg.set_consumer_key(consumer_key=app_keys['consumer_key'])
        lg.set_consumer_secret(consumer_secret=app_keys['consumer_secret'])
        lg.login()
        twit.set_auth_obj(obj=lg)

    if( p['count']>0 ):
        print "Requesting %d IDs per request"%(p['count'])
        twit.set_count(p['count'])

    if( p['uname'] ):
        print "Requesting user:",p['uname']
        twit.set_username(p['uname'])
    elif( p['uid'] ):
        print "Requesting UID:",p['uid']
        twit.set_user_id(long(p['uid']))
    else:
        print "Must supply a username or user id"
        return
    
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

    m = None
    count = 0
    total = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        m = twit.get_message()
        if( m ):
            count += 1
            #print m
            if( p['limits'] ):
                print "Limits:",twit.get_rate_limit(),twit._throttling()
            if( ("errors" in m) and m['errors'] ):
                error = m['errors'][0]
                print "\tError %d: %s"%(error['code'],error['message'])
            else:
                id_list = m['ids']
                total = total + len(id_list)
                if( p['json'] ):
                    print json.dumps(m, sort_keys=True, indent=4)
                else:
                    print "Messages: %d"%(count)
                    print id_list
                    print "IDs: %d Total IDs: %d"%(len(id_list),total)

    if( twit.had_warning() ):
        print "WARNING:",twit.get_last_warning()
    if( twit.had_error() ):
        print "ERROR:",twit.get_last_error()

    twit.terminate_thread()
    return

if __name__ == '__main__':
    main(sys.argv)
