#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: OAuthBase.py
#
#   A base class for assisting with oauth logins
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import os, gc, sys, datetime, time, logging, warnings 
import webbrowser
import requests
import requests_oauthlib
#from cStringIO import StringIO


class OAuthBase(object):
    def __init__(self, 
                 name="OAuthLogin",
                 app_name="Unknown_OAuth_Application",
                 app_user=None,
                 logger=None,
                 consumer_key=None,
                 consumer_secret=None,
                 token_fname=None,
                 token_dir=None):
        self.name = name
        self.app_name = app_name
        self.app_user = app_user
        self.requests_session = None
        if( token_fname ):
            self.token_fname = token_fname
        else:
            self.token_fname = "token.oauth"
        self.set_token_dir(token_dir=token_dir)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.logger = None
        if( logger ):
            self.logger = logger
        else:
            self.logger = logging.getLogger(self.name)
        self.authorize_url = None
        self.request_token_url = None
        self.access_token_url = None
        self.token_file_header = None
        self.oauth_token = None
        self.oauth_secret = None
        self.last_header = None
        self.debug = False

    def reset_requests_session(self):
        if( self.requests_session ):
            self.requests_session.close()
            self.requests_session = None
            gc.collect()
        self.requests_session = requests_oauthlib.OAuth1Session(client_key=self.consumer_key,
                                                      client_secret=self.consumer_secret,
                                                      resource_owner_key=self.oauth_token,
                                                      resource_owner_secret=self.oauth_secret)
        r_a1 = requests.adapters.HTTPAdapter(pool_connections=100,
                                             pool_maxsize=100,
                                             max_retries=3)
        r_a2 = requests.adapters.HTTPAdapter(pool_connections=100, 
                                             pool_maxsize=100,
                                             max_retries=3)
        self.requests_session.mount('http://', r_a1)
        self.requests_session.mount('https://', r_a2)
        return


    def set_debug(self, bug=True):
        self.debug = bug

    def set_app_name(self, app_name=None):
        self.app_name = app_name
    
    def set_app_user(self, app_user=None):
        self.app_user = app_user
    
    def __token_dir_path(self, path=None):
        # avoid clobbering an existing file
        if( not os.path.isfile(path) ):
            # not a file, maybe an existing dir
            if( not os.path.isdir(path) ):
                # not a file, not an existing dir, create
                os.mkdir(path)
    
    def set_token_dir(self, token_dir=None):
        if( token_dir ):
            self.token_dir = token_dir
            self.__token_dir_path(self.token_dir)
        else:
            #self.token_dir = os.environ['HOME']+os.sep+".oauth"
            self.token_dir = os.path.expanduser("~"+os.sep+".oauth")
            self.__token_dir_path(self.token_dir)
            if( self.app_user ):
                #self.token_dir = os.environ['HOME']+os.sep+".oauth"+os.sep+self.app_user
                self.token_dir = self.token_dir+os.sep+self.app_user
                self.__token_dir_path(self.token_dir)

    
    def set_consumer_key(self, consumer_key=None):
        self.consumer_key = consumer_key
    
    def set_consumer_secret(self, consumer_secret=None):
        self.consumer_secret = consumer_secret
    
    def set_request_token_url(self, url=None):
        self.request_token_url = url
    
    def set_access_token_url(self, url=None):
        self.access_token_url = url
    
    def set_authorize_url(self, url=None):
        self.authorize_url = url

    def read_token_file(self):
        #
        #
        fname = self.token_dir+os.sep+self.token_fname
        f = open(fname,"r")
        if( f ):
            if( self.debug ):
                print "Opening",fname
            line = f.readline()
            self.token_file_header = line.replace('\n','')
            if( self.debug ):
                print "header:",self.token_file_header
            line = f.readline()
            self.oauth_token = line.replace('\n','')
            if( self.debug ):
                print "oauth_token:",self.oauth_token
            line = f.readline()
            self.oauth_secret = line.replace('\n','')
            if( self.debug ):
                print "oauth_secret:",self.oauth_secret
            f.close()
            return [self.oauth_token, self.oauth_secret]
        else:
            return None
    
    def write_token_file(self):
        fname = self.token_dir+os.sep+self.token_fname
        dt = datetime.datetime.now()
        dtstr = dt.strftime("%b %d, %Y %H:%M:%S")
        self.token_file_header = "# Authorization for app \"%s\" at %s"%(self.app_name,dtstr)
        f = open(fname,"wb")
        f.write(self.token_file_header.encode('utf-8'))
        f.write("\n")
        f.write(str(self.oauth_token).encode('utf-8'))
        f.write("\n")
        f.write(str(self.oauth_secret).encode('utf-8'))
        f.write("\n")
        f.close()

    def has_user_app_tokens(self):
        # first see if we can simply read that token file and move on
        auths = None
        try:
            auths = self.read_token_file()
        except:
            auths = None
        if( auths ):
            #print "Have Auth Already"
            return True
        return False

    def login(self):
        # first see if we can simply read that token file and move on
        if( self.has_user_app_tokens() ):
            return True
        
        #print "Starting the auth"
        assert self.consumer_key is not None 
        assert self.consumer_secret is not None
        assert self.request_token_url is not None 
        assert self.authorize_url is not None 
        assert self.access_token_url is not None 
        
        ## USING self.request_token_url
        # create a local OAuth1Session helper
        oauth = requests_oauthlib.OAuth1Session(client_key=self.consumer_key,
                                                client_secret=self.consumer_secret)
        print "Requesting:",self.request_token_url
        token_resp = oauth.fetch_request_token(self.request_token_url)
        owner_oauth_token = token_resp.get('oauth_token')
        owner_oauth_token_secret = token_resp.get('oauth_token_secret')                                     
        authorize_url = self.authorize_url+'?oauth_token='+owner_oauth_token

        print
        print "You need to authorize the application",
        print "\"%s\" before you can use it."%(self.app_name)
        print
        print "A web browser should open requesting authorization. ",
        print "Once you have authorized the application please return here and ",
        print "enter the PIN code that you were provided."
        print
        print "If a web browser does not open please cut and paste this URL into",
        print "a browser to complete the authorization and retrieve a PIN."
        print
        print str(authorize_url)
        print
        ## the call to webbrowser.open(req_url) *always* generates an error message
        ## here we'll trap that text to make sure it doesn't display any more
        #
        ## This does not work, the error is coming from some sub-process thread
        #
        #mystdout = StringIO()
        #mystderr = StringIO()
        #old_stdout = sys.stdout
        #old_stderr = sys.stderr
        #sys.stdout = mystdout
        #sys.stderr = mystderr
        webbrowser.open(authorize_url)
        #sys.stdout = old_stdout
        #sys.stderr = old_stderr
        
        pin_verifier = raw_input('Please enter the PIN: ')
        
        if( not pin_verifier ):
            print "You MUST provide an authorization PIN"
            return False
        
        ## USING self.access_token_url
        # Now, using the PIN verification key request the permanent tokens
        oauth = requests_oauthlib.OAuth1Session(client_key=self.consumer_key,
                                                client_secret=self.consumer_secret,
                                                resource_owner_key=owner_oauth_token,
                                                resource_owner_secret=owner_oauth_token_secret,
                                                verifier=pin_verifier)
        oauth_tokens = oauth.fetch_access_token(self.access_token_url)
        self.oauth_token = oauth_tokens.get('oauth_token')
        self.oauth_secret = oauth_tokens.get('oauth_token_secret')

        self.write_token_file()
        return True


    def make_request(self, request=None):
        result = []
        if( not self.requests_session ):
            raise requests.exceptions.ConnectionError("Need OAuthSession - reset_requests_session()")
        if( request['method']=="POST" ):
            #print "OAUTH POST request:",request
            result = self.requests_session.post(request['domain'],
                                                params=request['params'],
                                                headers=request['headers'],
                                                data=request['payload'])
        else:
            #print "OAUTH GET request:",request
            result = self.requests_session.get(request['domain'],
                                               params=request['params'],
                                               headers=request['headers'])
        return result


def usage(argv):
    print "USAGE: python %s "%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 1:
        usage(argv)
    
    lg = OAuthBase( name="TestLoginObj",
                    app_name="INFX547Test01",
                    token_fname="OAuthBase_testing.oauth")
    lg.set_debug(True)
    lg.set_request_token_url(url='https://twitter.com/oauth/request_token')
    lg.set_access_token_url(url='https://twitter.com/oauth/access_token')
    lg.set_authorize_url(url='https://twitter.com/oauth/authorize')
    
    # KEYS FOR INFX547Test01
    # also "client_id" in the requests_oauthlib model
    lg.set_consumer_key(consumer_key='0pVJzx0aaQDri1kd3WQA')
    # also "client_secret" in the requests_oauthlib model
    lg.set_consumer_secret(consumer_secret='kUtAsuqjwTPYo2xpt7VZOoerXzCpM4JwAg8OCEbO0')

    print ">>> PERFORMING LOGIN <<<"
    if( lg.login() ):
        print ">>> Login appears successful! <<<"
    else:
        print ">>> Login appears to have FAILED! <<<"
    print ">>> DONE <<<"
    return

if __name__ == '__main__':
    main(sys.argv)   
