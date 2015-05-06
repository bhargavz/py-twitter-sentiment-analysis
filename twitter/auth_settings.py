#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: auth_settings.py
#
#   SETTINGS 
#   Configure the twitter application consumer_key and consumer_secret
#   pair that will be used by the local machine for authentication.
#   These pairs need to be passed to the local OAuth object when it is
#   created. See examples in specific application sections.
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.

import os, platform

# This gets the name of the local host
try:
    TWITTER_APP_LOCAL_HOST = platform.node().split('.')[0]
except:
    try:
        #TWITTER_APP_LOCAL_HOST = os.uname()[1].split('.')[0]
        TWITTER_APP_LOCAL_HOST = platform.uname()[1].split('.')[0]
    except:
        TWITTER_APP_LOCAL_HOST = 'localhost'
    

# A list of twitter users (usernames) that authenticate the possible
# twitter applications
TWITTER_USER_CONFIG = [
        "infxtweets"
    ]

# A list of twitter applications which a user might authenticate
TWITTER_APPLICATION_CONFIG = [
        "INFX547Test01", "INFX547Test02" ]

# This maps a specific twitter application to it's unique pair of
# consumer_key and consumer_secret. These have to be well known for
# each twitter application or there is no way for a local application
# to generate the user key and user secret
TWITTER_APP_OAUTH_CONFIG = { 
##
#   A pair of testing applications for INFX 547
##
    'INFX547Test01': 
       {'consumer_key':'<REMOVED>',
        'consumer_secret':'<REMOVED>'}, 
    'INFX547Test02': 
       {'consumer_key':'<REMOVED>',
        'consumer_secret':'<REMOVED>'}
}


# This returns the specific pair of key and secret for the specified app
def TWITTER_APP_OAUTH_PAIR(app=None):
    try:
        oauth_pair = TWITTER_APP_OAUTH_CONFIG[app]
    except KeyError:
        oauth_pair = TWITTER_APP_OAUTH_CONFIG["INFX547Test01"]
    return oauth_pair

# This returns the token name - used for storing the local user generated
# tokens
#TWITTER_APP_TOKEN_FNAME = TWITTER_APP_NAME+".oauth"
def TWITTER_APP_TOKEN_FNAME(app=None):
    return app+".oauth"


