#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: Login.py
#   DATE: April, 2012
#   Author: Bhargav Shah
#
#   A class for managing Twitter OAuth logins based on the common
#   OAuthBase class. Simply override the authorization URLs
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys
from sochi.common.OAuthBase import OAuthBase
from sochi.twitter.auth_settings import *

class Login(OAuthBase):
    def __init__(self, 
                 name="TwitterLogin",
                 app_name="Some_OAuth_Application",
                 app_user=None,
                 logger=None,
                 consumer_key=None,
                 consumer_secret=None,
                 token_fname=None,
                 token_dir=None):
        OAuthBase.__init__(self, name=name, app_name=app_name, 
                           app_user=app_user, logger=logger,
                           consumer_key=consumer_key, consumer_secret=consumer_secret,
                           token_fname=token_fname, token_dir=token_dir)
        self.authorize_url='https://twitter.com/oauth/authorize'
        self.request_token_url='https://twitter.com/oauth/request_token'
        self.access_token_url='https://twitter.com/oauth/access_token'




def parse_params(argv):
    auth = None
    user = None
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
        if( param == "-debug"):
            debug = True
        pc += 1
    
    return {'auth':auth, 'user':user, 'debug':debug }


def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> [-debug]"%(argv[0])
    sys.exit(0)

# Examples of commandline usage
#    python Login.py -auth INFX547Test01 -user sochitweets
#    python Login.py -auth INFX547Test02 -user sochitweets


def main(argv):
    if len(argv) < 4:
        usage(argv)
    p = parse_params(argv)
    print p
    
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return
    
    app = p['auth']
    app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
    app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
    lg = Login( name="TestLoginObj",
                app_name=p['auth'],
                app_user=p['user'],
                token_fname=app_token_fname)
    if( p['debug'] ):
        lg.set_debug(True)
    ## Key and secret for specified application
    lg.set_consumer_key(consumer_key=app_keys['consumer_key'])
    lg.set_consumer_secret(consumer_secret=app_keys['consumer_secret'])
    
    print ">>> PERFORMING LOGIN <<<"
    if( lg.login() ):
        print ">>> Login appears successful! <<<"
    else:
        print ">>> Login appears to have FAILED! <<<"
    print ">>> DONE <<<"
    return

if __name__ == '__main__':
    main(sys.argv)   
