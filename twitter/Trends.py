#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: Trends.py
#
#   An object for finding the current trending topics in Twitter. But this
#   also allows searching and finding the specific geographic regions where
#   trending topics could be found through the WOEID parameters supported by
#   Twitter.
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, random, logging
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class Trends(TwitterBase):
    def __init__(self, 
                 name="Trends",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                            args=args, kwargs=kwargs)
        self.trends_place_url ="https://api.twitter.com/1.1/trends/place.json"
        self.trends_available_url ="https://api.twitter.com/1.1/trends/available.json"
        self.trends_available = True
        self.set_request_type_as_trends_available()

    ##
    # Sets the domain to the trends for a specific place
    #
    def set_request_type_as_trends_place(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_rate_limit_resource("trends","place")
            self.set_request_domain(self.trends_place_url)
            self.trends_available = False

    ##
    # Finds the WOEID values that are supported by twitter
    #
    def set_request_type_as_trends_available(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_rate_limit_resource("trends","available")
            self.set_request_domain(self.trends_available_url)
            self.trends_available = True

    ##
    # Sets the Where On Earth ID (WOEID)
    # WOEID=1 is Global
    #
    def set_woeid(self, woeid=1):
        self.set_request_param(kw="id",val=str(woeid))

    ##
    # 
    #
    def make_request(self):
        # this code is not reentrant, don't make the request twice
        if( self.querying ):
            return

        self.querying = True
        try: 
            self.set_request(domain=self.get_request_domain(),
                                method="GET",
                                params=self.get_request_params())
            request_results = self._make_request(request=self._request_data)
            
            js = None
            if( request_results or request_results.text ):
                try:
                    js = request_results.json()
                except ValueError, e:
                    mesg = "JSON ValueError: "+str(e)
                    self.logger.info(mesg)
                    js = None

            if( js ):
                #print json.dumps(js, sort_keys=True, indent=4)
                if( self.trends_available ):
                    self.put_message(js)
                else:
                    ## This was a trends query
                    trend_list = js[0]['trends']
                    self.put_message(trend_list)
            self.querying = False
        except:
            self.querying = False
            raise
        return

def parse_params(argv):
    auth = None
    user = None
    woeid = None
    place = None
    limits = False
    json = False
    logging = False
    debug = False
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]

        if( param == "-woeid"):
            pc += 1
            woeid = argv[pc]
        if( param == "-w"):
            pc += 1
            woeid = argv[pc]
        if( param == "-place"):
            pc += 1
            place = argv[pc].lower()

        if( param == "-log"):
            logging = True
        if( param == "-json"):
            json = True
        if( param == "-limits"):
            limits = True
        if( param == "-debug"):
            debug = True
        pc += 1
    return {'auth':auth, 'user':user,
            'woeid':woeid, 'place_name':place,
            'logging':logging, 'limits':limits, 'debug':debug, 'json':json }


def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> [-woeid <woeid>] [-place <place_name>] [-json]"%(argv[0])
    sys.exit(0)

# Find all the woeid places in the US
#   python Trends.py -auth INFX547Test01 -user dwmcphd -place "United States"
# Find all the woeid places in India
#   python Trends.py -auth INFX547Test01 -user dwmcphd -place India
#
# Find the trending topics over the whole world
#   python Trends.py -auth INFX547Test01 -user dwmcphd -woeid 1
# Find the trending topics in Honolulu, Hawaii, USA
#   python Trends.py -auth INFX547Test01 -user dwmcphd -woeid 2423945


def main(argv):
    if len(argv) < 4:
        usage(argv)
    p = parse_params(argv)
    print p
    
    twit = Trends()
    twit.set_user_agent(agent="random")
    twit.set_throttling(True)

    if( p['logging'] ):
        log_fname = twit.get_preferred_logname()
        fmt='[%(asctime)s][%(module)s:%(funcName)s():%(lineno)d] %(levelname)s:%(message)s'
        logging.basicConfig(filename=log_fname,format=fmt,level=logging.INFO)
        log = logging.getLogger("twit_tools")

    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="TrendsLoginObj",
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

    have_woeid = False
    if( p['woeid'] ):
        twit.set_request_type_as_trends_place()
        twit.set_woeid(p['woeid'])    
        have_woeid = True
 
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
    p_tot = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        m = twit.get_message()
        if( m ):
            for item in m:
                tot += 1
                if( have_woeid ):
                    if( p['json'] ):
                        print json.dumps(item, sort_keys=True, indent=4)
                    else:
                        print "[%2d]"%(tot),item['name'].encode('utf-8')
                elif( p['place_name'] ):
                    lname = item['name'].lower()
                    cname = item['country'].lower()
                    if( lname.find(p['place_name'])>=0 or cname.find(p['place_name'])>=0 ):
                        p_tot += 1
                        if( p['json'] ):
                            print json.dumps(item, sort_keys=True, indent=4)
                        else:
                            print "[%3d]: -woeid %s"%(p_tot,str(item['woeid'])),
                            print "%s, %s (%s)"%(item['name'],item['country'],item['countryCode'])
                            #print item['name'].encode('utf-8'),
                            #print item['country'].encode('utf-8')
                else:
                    if( p['json'] ):
                        print json.dumps(item, sort_keys=True, indent=4)
                    else:
                        print "[%3d]: -woeid %s"%(tot,str(item['woeid'])),
                        print "%s, %s (%s)"%(item['name'],item['country'],item['countryCode'])
                        #print item['name'].encode('utf-8'),
                        #print item['country'].encode('utf-8')

    if( p['place_name'] ):
        print "Found %d matching places."%(p_tot)
    print "Total items retrieved: %d"%(tot)

    if( p['limits'] ):
        print "Limits:",twit.get_rate_limit(),twit._throttling()

    return

if __name__ == '__main__':
    main(sys.argv)   
