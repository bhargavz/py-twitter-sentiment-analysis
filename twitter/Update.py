#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: Update.py
#
#   This class provides mechanisms to update, reply to, retweet status
#   messages and send direct messages
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, logging
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class Update(TwitterBase):
    def __init__(self, 
                 name="Update",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                              args=args, kwargs=kwargs)
        self.update_url ="https://api.twitter.com/1.1/statuses/update.json"
        self.retweet_url ="https://api.twitter.com/1.1/statuses/retweet/"
        self.direct_url ="https://api.twitter.com/1.1/direct_messages/new.json"
        self.status_update = False
        self.status_retweet = False
        self.direct_message = False
        self.max_status_len = 140
        self.set_request_type_as_status_update()

    ##
    # Sets the type of request to a status update
    #
    def set_request_type_as_status_update(self):
        if( not self.querying ):
            self.status_update = True
            self.status_retweet = False
            self.direct_message = False
            self.clear_request_params()
            self.set_request_domain(self.update_url)

    ##
    # Sets the type of request to a retweet request
    #
    def set_request_type_as_retweet(self):
        if( not self.querying ):
            self.status_update = False
            self.status_retweet = True
            self.direct_message = False
            self.clear_request_params()
            self.set_request_domain(self.retweet_url)

    ##
    # Sets the type of request to direct message
    #
    def set_request_type_as_direct_message(self):
        if( not self.querying ):
            self.status_update = False
            self.status_retweet = False
            self.direct_message = True
            self.clear_request_params()
            self.set_request_domain(self.direct_url)

    ##
    # Sets the status to be set when the request is made
    #
    def set_status(self, status=None, doit=False):
        if( not self.querying ):
            if( status and self.status_update):
                status = self._trim_status(status)
                self.set_request_param(kw="status", val=status)
                if( doit ):
                    if( self.running ):
                        self.start_request()
                    else:
                        self.make_request()
            else:
                self.clear_request_params()

    ##
    # Sets whether or not this status message is in reply to another message
    #
    def set_in_reply_to(self, status_id=None):
        if( not self.querying ):
            if( status_id and self.status_update):
                self.set_request_param(kw="in_reply_to_status_id", val=str(status_id))
            else:
                self.clear_request_params()

    ##
    # Sets the latitude and longitude
    #
    def set_location(self, lat=None, lon=None):
        if( not self.querying ):
            if( lat and lon and self.status_update ):
                self.set_request_param(kw="lat", val=str(lat))
                self.set_request_param(kw="long", val=str(lon))
            else:
                self.clear_request_params()

    ##
    # Sets the status to be an @ reply to the specified user
    #
    def set_at_reply_message(self, username=None, status=None, doit=False):
        if( not self.querying ):
            if( user and status and self.status_update ):
                status = "@"+str(username)+" "+str(status)
                status = self._trim_status(status)
                self.set_request_param(kw="status", val=status)
                if( doit ):
                    if( self.running ):
                        self.start_request()
                    else:
                        self.make_request()
            elif( status ):
                self.set_status(status=status,doit=doit)
            else:
                self.clear_request_params()

    ##
    # Sets a direct message to be sent to a specific user either using
    # username or user_id
    #
    def set_direct_message(self, username=None, user_id=None, status=None, doit=False):
        if( not self.querying ):
            if( (username or user_id) and status and self.direct_message ):
                status = self._trim_status(status)
                self.set_request_param(kw="text", val=status)
                if( username ):
                    self.set_request_param(kw="screen_name", val=username)
                if( user_id ):
                    self.set_request_param(kw="user_id", val=user_id)
                if( doit ):
                    if( self.running ):
                        self.start_request()
                    else:
                        self.make_request()
            else:
                self.clear_request_params()

    ##
    # Will retweet the specified tweet ID
    #
    def set_retweet(self, tweet_id=None, doit=False):
        if( not self.querying ):
            if( tweet_id and self.status_retweet ):
                url = self.retweet_url+str(tweet_id)+".json"
                self.clear_request_params()
                self.set_request_domain(url)
                if( doit ):
                    if( self.running ):
                        self.start_request()
                    else:
                        self.make_request()
            else:
                self.clear_request_params()

    ##
    # Trim the status message to fit 140 character limit of Twitter
    #
    def _trim_status(self, status=None):
        if( status ):
            status = unicode(status)
            if( len(status) > self.max_status_len ):
                mesg = "Status too long, truncated."
                self.logger.info(mesg)
                mesg = "Old status: \"%s\""%(status)
                self.logger.info(mesg)
                status = status[:self.max_status_len]
                mesg = "New status: \"%s\""%(status)
                self.logger.info(mesg)
        return status

    ##
    # Basically a cheap version of make_request for a status update
    #
    def update_status(self):
        if( self.running ):
            self.start_request()
        else:
            self.make_request()

    ##
    # 
    #
    def make_request(self):
        # this code is not reentrant, don't make the request twice
        if( self.querying ):
            return

        self.querying = True            
        try:
            # this must be a POST request as defined by the "Update" spec
            #print "domain",self.get_request_domain()
            #print "payload",self.get_request_params()
            self.set_request(domain=self.get_request_domain(),
                             method="POST",
                             payload=self.get_request_params())
            request_results = self._make_request(request=self._request_data)
            js = None
            if( request_results or request_results.text ):
                try:
                    #print request_results.text
                    js = request_results.json()
                except ValueError, e:
                    mesg = "JSON ValueError: "+str(e)
                    self.logger.info(mesg)
                    js = None
            if( js ):
                #print json.dumps(js, sort_keys=True, indent=4)
                self.put_message(m=js)
            self.querying = False
        except:
            self.querying = False
            raise
        return


def parse_params(argv):
    auth = None
    user = None
    status = None
    direct = None
    retweet = None
    favorite = None
    json = False
    limits = False
    debug = False
    logging = False
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]

        if( param == "-status"):
            pc += 1
            status = argv[pc]
        if( param == "-s"):
            pc += 1
            status = argv[pc]

        if( param == "-direct"):
            pc += 1
            direct = argv[pc]
        if( param == "-d"):
            pc += 1
            direct = argv[pc]
        if( param == "-retweet"):
            pc += 1
            retweet = argv[pc]
        if( param == "-r"):
            pc += 1
            retweet = argv[pc]
        if( param == "-favorite"):
            pc += 1
            favorite = argv[pc]
        if( param == "-f"):
            pc += 1
            favorite = argv[pc]

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
            'status':status, 'direct':direct, 'retweet':retweet, 'favorite':favorite,
            'logging':logging, 'debug':debug, 'json':json, 'limits':limits }



def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> -status \"<message>\" [-direct <username>] [-retweet <tweet_id>] [-log] [-json] "%(argv[0])
    sys.exit(0)

def main(argv):
    if len(argv) < 4:
        usage(argv)
    p = parse_params(argv)
    print p

    twit = Update()
    twit.set_user_agent(agent="random")

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
        lg = Login( name="StatusUpdateLogin",
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

    if( p['retweet'] ):
        twit.set_request_type_as_retweet()
        twit.set_retweet(tweet_id=p['retweet'])
    elif( p['direct'] and p['status']):
        twit.set_request_type_as_direct_message()
        twit.set_direct_message(status=p['status'],username=p['direct'])
    elif( p['status'] ):
        twit.set_request_type_as_status_update()
        twit.set_status(status=p['status'])
    else:
        print "Must supply a status message to post!"
        return
    
    twit.update_status()
    twit.wait_request()

    if( twit.messages()>0 ):
        m = twit.get_message()
        if( m ):
            if( p['json'] ):
                print json.dumps(m,indent=4,sort_keys=True)
            else:
                if( "created_at" in m and "user" in m ):
                    print "At %s, user %s posted:"%(m['created_at'],m['user']['name'])
                    print m['text'].encode('utf-8')
                elif( "error" in m or "errors" in m ):
                    print "Error response."
                else:
                    print "Not clear what this response was!"
                    print json.dumps(m,indent=4,sort_keys=True)
    else:
        print "Nothing returned!"
    
    if( twit.had_warning() ):
        print "WARNING:",twit.get_last_warning()
    if( twit.had_error() ):
        print "ERROR:",twit.get_last_error()

    return

if __name__ == '__main__':
    main(sys.argv)
