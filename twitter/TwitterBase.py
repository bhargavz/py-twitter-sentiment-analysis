#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: TwitterBase.py
#
#   A simple example of making a web service call using Twitter API
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, random, logging
import requests
from requests.exceptions import HTTPError, URLRequired
from datetime import datetime
from sochi.twitter.Login import Login
from sochi.twitter.auth_settings import *
from sochi.common.Base import Base

class TwitterBase(Base):
    def __init__(self, 
                 name="Trends",
                 logger=None,
                 args=(),
                 kwargs={}):
        Base.__init__(self, name=name, logger=logger,
                            args=args, kwargs=kwargs)
        # The URL to check the rate limit status
        self.rate_limit_url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
        self.rate_limits = None
        self.rate_limit_resource = "search"
        self.rate_limit_type = "tweets"
        self.pref_logname = "twit_tools.log"
        self.continuation_url = None
        self.continuation = False
        self.continuation_max = 10
        self.continuation_throttle_max = 10
        self.continuation_throttle_set = True
        self.continuation_count = 0

    ##
    # Gets the preferred log name for a log
    #
    def get_preferred_logname(self):
        return self.pref_logname

    ##
    # Sets the preferred log name for a log
    #
    def set_preferred_logname(self, fname="twit_tools.log"):
        self.pref_logname = fname

    ##
    # Sets the resource for the rate limit request on this object
    # this is really useful for subclassing
    #
    def set_rate_limit_resource(self, resource="search", resource_type="tweets"):
        self.rate_limit_resource = resource
        self.rate_limit_type = resource_type

    ##
    # Returns the current rate limit given a resource and resource type
    # See the get rate limit documentation on the Twitter API for
    # resource and resource types
    #
    def get_rate_limit(self, resource=None, resource_type=None, calls=3):
        result = []
        request_results = None
        self.warning_or_error = False
        try:
            if( not resource ):
                resource = self.rate_limit_resource
            if( not resource_type ):
                resource_type = self.rate_limit_type
            rl_request_data = {}
            rl_request_data['domain'] = self.rate_limit_url+"?resources="+resource
            rl_request_data['params'] = None
            rl_request_data['method'] = None
            rl_request_data['headers'] = None
            rl_request_data['payload'] = None
            #uri = self.rate_limit_url+"?resources="+resource
            request_results = super(TwitterBase,self)._make_request(request=rl_request_data,calls=calls)
            #print "URI:",uri
            #print "RESULTS:",request_results.text
        #except requests.exceptions.HTTPError, err:
        except HTTPError, err:
            mesg = "Twitter HTTP %s Error, during rate limit request"%(str(err.getcode()))
            self.logger.info(mesg)
            ## if we get an HTTP error then make up to 3 attempts
            if( calls>0 ):
                time.sleep(0.731)
                result = self.get_rate_limit(resource=resource,
                                             resource_type=resource_type,
                                             calls=(calls-1))
                request_results = None
            else:
                raise err
        #except requests.exceptions.URLRequired, err:
        except URLRequired, err:
            mesg = "URL Error %s, during rate limit request"%(str(err.getcode()))
            self.logger.info(mesg)
            raise err

        #print "RESULTS:",request_results.text
        if( request_results or request_results.text ):
            try:
                js = request_results.json()
            except ValueError, ve:
                #print str(ve)
                mesg = "get_rate_limit() Problem with JSON"
                self.logger.info(mesg)
                self.logger.info(request_results.text)                
                js = None
                return None
            
            rinfo = self.get_request_info()
            if( rinfo ):
                rinfo['next_results'] = None
                rinfo['refresh_url'] = None
                replwarn = self.get_header_value(headers=request_results.headers,key="X-Warning:")                        
                if( replwarn ):
                    rinfo['warning'] = replwarn
                    self.warning_or_error = True
                    self.last_warning_message = replwarn
                if( "errors" in js ):
                    rinfo['error'] = js['errors'][0]
                    self.warning_or_error = True
                    self.last_warning_message = js['errors'][0]
                    return None
            
            #print "IN get_rate_limit"
            #print json.dumps(js, sort_keys=True, indent=4)
            url = "/"+resource+"/"+resource_type
            remaining_hits = js['resources'][resource][url]['remaining']
            reset_at = js['resources'][resource][url]['reset']
            reset_in_sec = (reset_at-int(time.time()))
            reset_in_min = reset_in_sec/60
            #print "reset_at:", reset_at
            #print "reset_in_sec:", reset_in_sec
            #print "reset_in_min:", reset_in_min
            result = [reset_at, reset_in_sec, reset_in_min, remaining_hits, 
                      "resource:"+"/"+resource+"/"+resource_type]
            self.rate_limits = result
        return result

    ##
    # How long a thread might wait - is called by the self._throttleQueries
    # when a self._makeRequest is actually made
    #
    def _throttling(self, qs=None):
        waits = 0.0
        if( self.throttling ):
            waits = 4.0
            if( self.rate_limits ):
                if( not self.rate_limits[0] ):
                    limits = self.get_rate_limit()
                if( self.rate_limits[1]<0 ):
                    return 60.0
                if( self.rate_limits[3]<2 ):
                    waits = float(self.rate_limits[1])+1.0
                else:
                    waits = float(self.rate_limits[1])/float(self.rate_limits[3])+1.0
        return waits

    ##
    # Override of the base class handler for Twitter specific
    # messages - the move to the Requests framework makes this less
    # important. It would be good to re-integrate this code under Requests
    #
    def handle_http_error(self, err=None, wait=7, auth=False):
        assert err is not None
        if err.getcode() in [300, 301, 302, 303, 304, 305, 306, 307]:
            mesg = "Twitter %s Error (handled:True)"%(str(err.getcode()))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return True
        if err.getcode() in [402, 405, 406]:
            mesg = "Twitter %s Error (handled:True)"%(str(err.getcode()))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return True
        if err.getcode()==401:
            # probably ought to just skip this item
            if( auth ):
                mesg = "Twitter 401 Error, Authentication required (handled:False)"
                self.logger.info(mesg)
                #self.logger.info(err.strerror)
                ## need to authenticate!
                return False
            else:
                mesg = "Twitter 401 Error, Authentication required (handled:False)"            
                self.logger.info(mesg)
                #self.logger.info(err.strerror)
                return False
            return False
        elif err.getcode()==403:
            mesg = "Twitter %d Error, Update limited, sleeping %ss (handled:True)"%(err.getcode(),str(wait))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            time.sleep(wait)
            return True
        elif err.getcode()==404:
            mesg = "Twitter 404 Error, Not Found, bad URI (handled:True)?"
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return True
        elif err.getcode()==400:
            mesg = "Twitter 400 Error, rate limit, waiting %ss (handled:True)"%(str(360.0))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            time.sleep(360.0)
            return True
        elif err.getcode()==420:
            mesg = "Twitter 420 Error, enhancing calm for %ss (handled:True)"%(str(360.0))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            time.sleep(360.0)
            return True
        elif err.getcode() in [500, 501, 502, 503, 504]:
            mesg = "Twitter %d Error, sleep %ss"%(err.getcode(),str(wait))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            time.sleep(wait)
            return True
        else:
            return False
        return False


    ##
    # Sets the status of whether or not to use a continuation URL
    # If twitter responds with a continuation URL
    #
    def set_continuation(self,c=False):
        self.continuation = c

    def reset_continuation(self):
        self.continuation_url = None

    def get_continuation(self):
        response = None
        self.continuation_url = None
        rinfo = self.get_request_info()
        if( rinfo ):
            if( rinfo['next_results'] ):
                response = rinfo['next_results']
                if( self.continuation ):
                    self.continuation_url = rinfo['next_results']
        return response


    def had_warning(self):
        rinfo = self.get_request_info()
        if( rinfo and ("warning" in rinfo) ):
            if( rinfo['warning'] ):
                return True
        return False
        
    def get_last_warning(self):
        rinfo = self.get_request_info()
        if( rinfo and ("warning" in rinfo) ):
            return rinfo['warning']
        return None


    def had_error(self):
        rinfo = self.get_request_info()
        if( rinfo and ("error" in rinfo) ):
            if( rinfo['error'] ):
                return True
        return False
        
    def get_last_error(self):
        rinfo = self.get_request_info()
        if( rinfo and ("error" in rinfo) ):
            return rinfo['error']
        return None


    def _make_request(self, request=None, calls=4):
        assert request is not None
        self.warning_or_error = False
        request_results = []
        request_results = super(TwitterBase,self)._make_request(request=request,calls=calls)
        
        rinfo = self.get_request_info()
        if( rinfo ):
            rinfo['next_results'] = None
            rinfo['refresh_url'] = None
            replwarn = self.get_header_value(headers=request_results.headers,key="X-Warning:")                        
            if( replwarn ):
                rinfo['warning'] = replwarn
                self.warning_or_error = True
                self.last_warning_message = replwarn
            try:
                meta = None
                try:
                    js = request_results.json()
                except ValueError, e:
                    mesg = "JSON ValueError: "+str(e)
                    self.logger.info(mesg)
                    js = None
                #print "IN TwitterBase._make_request()"
                #print json.dumps(js, sort_keys=True, indent=4)
                #if( js and type(js) == list ):
                #    print "LIST"
                #    print "LENGTH:",len(js)
                #    print json.dumps(js[0], sort_keys=True, indent=4)
                if( js and type(js) == dict ):
                    if( "errors" in js or "error" in js ):
                        try:
                            # if multiple errors grab the first one
                            rinfo['error'] = js['errors'][0]
                            self.last_warning_message = js['errors'][0]
                        except:
                            # if one error grab that one
                            rinfo['error'] = js['error']
                            self.last_warning_message = js['error']
                        self.warning_or_error = True
                        self.querying = False
                    keys = js.keys()
                    for k in keys:
                        if( k.find("metadata")>0 ):
                            meta = js[k]
                            break
                    if( meta ):
                        if( "next_results" in meta ):
                            rinfo['next_results'] = meta['next_results']
                        if( "refresh_url" in meta ):
                            rinfo['refresh_url'] = meta['refresh_url']
            except ValueError:
                raise
        
        #   X-Rate-Limit-Limit: the rate limit ceiling for that given request
        #   X-Rate-Limit-Remaining: the number of requests left for the 15 minute window
        #   X-Rate-Limit-Reset: the remaining window before the rate limit resets in UTC epoch seconds
        limit_header = self.get_header_value(headers=request_results.headers,key="X-Rate-Limit-Limit:")
        remaining_hits_header = self.get_header_value(headers=request_results.headers,key="X-Rate-Limit-Remaining:")
        reset_at_header = self.get_header_value(headers=request_results.headers,key="X-Rate-Limit-Reset:")
        if( limit_header ):
            limit = int(limit_header)
        else:
            limit = None
        if( remaining_hits_header ):
            remaining_hits = int(remaining_hits_header)
        else:
            remaining_hits = 90
        if( reset_at_header ):
            reset_at = int(reset_at_header)
            reset_in_sec = (reset_at-int(time.time()))
            reset_in_min = reset_in_sec/60
        else:
            reset_at = -1
            reset_in_sec = 400
            reset_in_min = reset_in_sec/60
        #print "reset_at:", reset_at
        #print "reset_in_sec:", reset_in_sec
        #print "reset_in_min:", reset_in_min
        self.rate_limits = [reset_at, reset_in_sec, reset_in_min, remaining_hits]
        return request_results


    ##
    # 
    #
    def make_request(self):
        try: 
            self.querying = True
            self.set_throttling(True)
            print "Limits:",self.get_rate_limit()
            if( self.had_warning() ):
                print "WARNING:",self.get_last_warning()
            if( self.had_error() ):
                print "ERROR:",self.get_last_error()
            print "Wait:",self._throttling()
            self.querying = False
        except:
            self.querying = False
            raise
        return



def parse_params(argv):
    auth = None
    user = None
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-query"):
            pc += 1
            query = argv[pc]
        if( param == "-size"):
            pc += 1
            size = int(argv[pc])
        if( param == "-count"):
            pc += 1
            size = int(argv[pc])
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]
        if( param == "-log"):
            logging = True
        pc += 1
    return { 'auth':auth, 'user':user }

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user>"%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 5:
        usage(argv)
    p = parse_params(argv)
    print p
    
    twit = TwitterBase()
    twit.set_user_agent(agent="ie")
    
    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="TestLoginObj",
                    app_name=p['auth'],
                    app_user=p['user'],
                    token_fname=app_token_fname)
        #lg.set_debug(True)
        ## Key and secret for specified application
        lg.set_consumer_key(consumer_key=app_keys['consumer_key'])
        lg.set_consumer_secret(consumer_secret=app_keys['consumer_secret'])
        lg.login()
        twit.set_auth_obj(obj=lg)

    twit.make_request()
    return

if __name__ == '__main__':
    main(sys.argv)   
