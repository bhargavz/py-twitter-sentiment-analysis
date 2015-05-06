#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: Search.py
#
#   A base class for making Search requests against the Twitter REST search API
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, logging
import json
# The native JSON decoder is "slow" - should check to see if one of these
# alternatives is faster. Maybe explore these at some point.
#
# "cjson" is a JSON decoder written in C linked to Python
#import cjson as json
# "ujson" is an alternate JSON decoder written in C linked to Python
#import ujson as json
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class Search(TwitterBase):
    def __init__(self, 
                 name="Search",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                              args=args, kwargs=kwargs)
        self.search_url ="https://api.twitter.com/1.1/search/tweets.json"
        self.set_request_type_as_search()
        
    ##
    # Sets the domain to the general search interface
    #
    def set_request_type_as_search(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_request_domain(self.search_url)
            self.set_rate_limit_resource("search","tweets")

    ##
    # Reset everything about this search object
    #
    def reset(self):
        self.set_request_type_as_search()

    ##
    # Sets the number of items to retrieve per page
    #
    def set_page_size(self, sz=100):
        # the maximum is 100
        try:
            size = int(sz)
        except:
            # No param means default will be 15
            self.remove_request_param(kw="count")
            return
        if( size > 100 ):
            size = 100
        if( size < 1 ):
            size = 1
        self.set_request_param(kw="count",val=str(size))
        return

    ##
    # Sets the number of items to retrieve per page
    #
    def set_count(self, c=100):
        self.set_page_size(sz=c)

    ##
    # Sets a simple Twitter query string
    #
    def set_query_terms(self, t=None):
        self.set_request_param(kw="q",val=t)

    ##
    # Returns the simple Twitter query string
    #
    def get_query_terms(self):
        return self.get_request_param(kw="q")

    ##
    # Sets a language specifier for a given query, to search for
    # responses with a given language
    #
    def set_query_lang(self, l=None):
        if( l ):
            self.set_request_param(kw="lang",val=l)
        else:
            self.remove_request_param(kw="lang")
        return

    ##
    # Sets a simple Twitter query string
    # q=twitterapi&until=2011-05-09
    #       containing "twitterapi" and sent before "2011-05-09"
    #
    def set_query_until(self, u=None):
        if( u ):
            self.set_request_param(kw="until",val=u)
        else:
            self.remove_request_param(kw="until")
        return

    ##
    # Sets a simple Twitter query string
    # q=superhero&since_id=1487356093
    #       containing "superhero" and sent since "1487356093" (a tweet id)
    #
    def set_query_since_id(self, s=None):
        if( s ):
            self.set_request_param(kw="since_id",val=str(s))
        else:
            self.remove_request_param(kw="since_id")
        return

    ##
    # Sets a simple Twitter query string
    # q=superhero&max_id=1487356093
    #       containing "superhero" and sent since "1487356093" (a tweet id)
    #
    def set_query_max_id(self, m=None):
        if( s ):
            self.set_request_param(kw="max_id",val=str(m))
        else:
            self.remove_request_param(kw="max_id")
        return

    ##
    # Sets a Twitter query geocode parameter for the query
    # The parameter is specified by "latitude,longitude,radius"
    # Example Values: 37.781157,-122.398720,1mi
    #
    def set_geocode(self, lat=None, lon=None, rad=25, units="mi"):
        if( lat and lon ):
            qs = "%s,%s,%s%s"%(str(lat),str(lon),str(rad),units)
            self.set_request_param(kw="geocode",val=qs)
        else:
            self.remove_request_param(kw="geocode")

    ##
    # Set whether or not to include entities in the search query
    #
    def set_include_entities(self, e=None):
        if( e ):
            self.set_request_param(kw="include_entities",val="true")
        elif( e==False ):
            self.set_request_param(kw="include_entities",val="false")
        else:
            self.remove_request_param(kw="include_entities")

    ##
    # Sets a simple Twitter query string
    # result_type=mixed     a mix of "popular" and "recent" tweets (default)
    # result_type=recent    return only the most "recent" tweets meeting the criteria
    # result_type=popular   return only the most "popular" tweets meeting the criteria
    #
    def set_query_result_type(self, rt=None):
        if( rt ):
            if( rt=="popular" ):
                self.set_request_param(kw="result_type",val="popular")
            elif( rt=="mixed" ):
                self.set_request_param(kw="result_type",val="mixed")
            elif( rt=="recent" ):
                self.set_request_param(kw="result_type",val="recent")
            else:
                self.set_request_param(kw="result_type",val=None)
        else:
            self.set_request_param(kw="result_type",val=None)

    ##
    # 
    #
    def make_request(self):
        # this code is not reentrant, don't make the request twice
        if( self.querying ):
            return

        self.querying = True
        # save throttling state
        throttling_save = self.throttling
        self.warning_or_error = False
        self.last_warning_message = {}
        
        try:
            self.continuation_count = 0
            p_stat = ""
            stat = "starting"

            # set the maximum number of continuation requests
            # this is dependent on the number of request still available in
            # the self.rate_limit list
            #print "rate_limits: ",self.rate_limits
            # start assuming the max we could have
            self.continuation_throttle_max = self.continuation_max
            if( self.continuation and self.rate_limits ):
                if( self.rate_limits[3]<self.continuation_max ):
                    self.continuation_throttle_max = self.rate_limits[3]
                    if( self.debug_output ):
                        print "Too few requests for continuation (%d):"%(self.continuation_throttle_max),
                        print self.rate_limits
            
            # if we're going to do some continuation requests, then don't throttle those
            if( self.continuation_count and self.continuation_throttle_max>0 ):
                self.throttling = False
            
            # now make sure we don't have a leftover continuation url
            self.reset_continuation()

            while( stat and self.continuation_count<self.continuation_throttle_max ):
                if( self.continuation and self.get_continuation() ):
                    url = self.get_request_domain()+self.get_continuation()
                    self.set_request(domain=url,
                                    method="GET")
                    if( self.debug_output ):
                        print "CONTINUATION REQUEST:"
                        print json.dumps(self._request_data, sort_keys=True, indent=4)
                else:
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
    
                if( js and ('statuses' in js) ):
                    results_list = []
                    #print "IN make_request()"
                    #print json.dumps(js, sort_keys=True, indent=4)
                    results_list = js['statuses']
                    # don't bother to add this if it's an empty list
                    if( len(results_list) > 0 ):
                        self.put_message(m=results_list)
                        rinfo = self.get_request_info()
                        if( rinfo ):
                            rinfo['success']=True

                p_stat = stat
                if( self.continuation ):
                    stat = self.get_continuation()
                    self.continuation_count += 1
                else:
                    stat = None
            self.querying = False
            self.throttling = throttling_save
        except:
            self.querying = False
            self.throttling = throttling_save
            raise
        return

def parse_params(argv):
    auth = None
    user = None
    query = None
    size = 4
    lang = None

    limits = False
    continuation = False
    logging = False
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
        if( param == "-size"):
            pc += 1
            size = int(argv[pc])
        if( param == "-count"):
            pc += 1
            size = int(argv[pc])
        if( param == "-lang"):
            pc += 1
            lang = argv[pc]
        
        if( param == "-log"):
            logging = True
        if( param == "-limits"):
            limits = True
        if( param == "-cont"):
            continuation = True
        if( param == "-debug"):
            debug = True
        if( param == "-json"):
            json = True
        pc += 1

    return {'auth':auth, 'user':user,
            'query':query, 'size':size, 'lang':lang,
            'limits':limits, 'json':json, 'logging':logging, 
            'use_continuations':continuation, 'debug':debug }

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> -query \"<query_terms>\" [-size <count>] [-lang <language_code>] [-cont] [-debug] [-json]"%(argv[0])
    sys.exit(0)

def main(argv):
    if len(argv) < 5:
        usage(argv)
    p = parse_params(argv)
    print p
    
    twit = Search()
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
        lg = Login( name="SearchLoginObj",
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

    if( p['lang'] ):
        twit.set_query_lang(p['lang'])

    print "Query Term", p['query']
    twit.set_query_terms(p['query'].encode('utf-8'))
    twit.set_page_size(sz=p['size'])
    twit.set_query_result_type(rt="recent")
    #twit.set_continuation(True)

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
    tot = 0
    tweet_count = 0
    mesg_count = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        m = twit.get_message()
        mesg_count += 1
        if( m ):
            tot = tot + len(m)
            #print json.dumps(m, sort_keys=True, indent=4)
            for rec in m:
                tweet_count += 1
                if( p['json'] ):
                    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count)
                    print json.dumps(rec, sort_keys=True, indent=4)
                else:
                    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count),
                    print rec['user']['screen_name'].encode('utf-8'),rec['user']['name'].encode('utf-8'),
                    print ":",rec['text'].encode('utf-8')
                    print
        while( twit.messages()<1 and twit.query_in_process() ):
            time.sleep(2)
    
    if( twit.had_warning() ):
        print "WARNING:",twit.get_last_warning()
    if( twit.had_error() ):
        print "ERROR:",twit.get_last_error()

    print "Continuation URL:",twit.get_continuation()
    print "Total tweets: ",tot

    if( p['limits'] ):
        print "Limits:",twit.get_rate_limit(),twit._throttling()

    twit.terminate_thread()
    return

if __name__ == '__main__':
    main(sys.argv)
