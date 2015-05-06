#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: UserLookup.py
#   An example object designed to return fully qualified User records
#   for the specified user screen names or user IDs. Currently, twitter
#   restricts this to 100 users per request.
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, json, logging
from threading import Semaphore
from sochi.twitter.Login import Login
from sochi.twitter.TwitterBase import TwitterBase
from sochi.twitter.auth_settings import *

class UserLookup(TwitterBase):
    def __init__(self, 
                 name="UserLookup",
                 logger=None,
                 args=(),
                 kwargs={}):
        TwitterBase.__init__(self, name=name, logger=logger,
                              args=args, kwargs=kwargs)
        self.userlookup_url ="https://api.twitter.com/1.1/users/lookup.json"
        self.set_request_domain(self.userlookup_url)
        self.set_rate_limit_resource("users","lookup")
        self.usem = Semaphore(1) # semaphore for the username/userid lists
        self.username_list = []
        self.user_id_list = []
        self.make_request_at = 100
        self.max_request = 100
        self.make_post_at = 20

    ##
    # Sets the domain to the general search interface
    #
    def set_request_type_as_userlookup(self):
        if( not self.querying ):
            self.clear_request_params()
            self.set_request_domain(self.userlookup_url)
            self.set_rate_limit_resource("users","lookup")
            self.username_list = []
            self.user_id_list = []
            self.make_request_at = 100
            self.max_request = 100
            self.make_post_at = 20

    ##
    # Sets the threshold for generating an automatic request. When
    # this number of user ids or usernames have been added then the
    # code automatically makes a request and stores the response
    #
    def set_request_threshold(self, t=100):
        if( (t>=1) and (t<=self.max_request) ):
            self.make_request_at = t
        else:
            self.make_request_at = self.max_request

    ##
    # Sets the threshold of usernames or user IDs at which the code switches
    # to a POST rather than a GET request
    #
    def set_post_threshold(self, t=20):
        if( (t>1) and (t<self.max_request) ):
            self.make_post_at = t
        else:
            self.make_post_at = 20

    ##
    # Add a user name to the list of users that will be requested
    #
    def add_username(self, un=None):
        if( self.querying ):
            return False
        self.usem.acquire()
        if( type(un) is list ):
            self.username_list.extend(un)
        else:
            self.username_list.append(un)
        self.usem.release()
        if( (len(self.username_list)+len(self.user_id_list)) >= self.make_request_at ):
            if( self.running ):
                self.start_request()
            else:
                self.make_request()
        return True

    ##
    # Add a user ID to the list of users that will be requested
    #
    def add_user_id(self, uid=None):
        if( self.querying ):
            return False
        self.usem.acquire()
        if( type(uid) is list ):
            uid_str = [str(x) for x in uid]
            self.user_id_list.extend(uid_str)
        else:
            self.user_id_list.append(str(uid))
        self.usem.release()
        if( (len(self.username_list)+len(self.user_id_list)) >= self.make_request_at ):
            if( self.running ):
                self.start_request()
            else:
                self.make_request()
        return True

    ##
    # Returns a request string of comma separated usernames
    #
    def _get_username_request_string(self, unmax=100):
        unStr = ""
        count = 0
        self.usem.acquire()
        if( (len(self.username_list)>0) and (count<unmax) ):
            count = 1
            unStr = self.username_list[0]
            self.username_list = self.username_list[1:]
            while( (len(self.username_list)>0) and (count<unmax) ):
                count += 1
                unStr = unStr+","+self.username_list[0]
                self.username_list = self.username_list[1:]
        self.usem.release()
        return [unStr,count]

    ##
    # Returns a request string of comma separated user IDs
    #
    def _get_user_id_request_string(self, uidmax=100):
        uidStr = ""
        count = 0
        self.usem.acquire()
        if( (len(self.user_id_list)>0) and (count<uidmax) ):
            count = 1
            uidStr = self.user_id_list[0]
            self.user_id_list = self.user_id_list[1:]
            while( (len(self.user_id_list)>0) and (count<uidmax) ):
                count += 1
                uidStr = uidStr+","+self.user_id_list[0]
                self.user_id_list = self.user_id_list[1:]
        self.usem.release()
        return [uidStr,count]

    ##
    # 
    #
    def make_request(self):
        # this code is not reentrant, don't make the request twice
        if( self.querying ):
            return
        
        # ok, we're not already querying
        self.querying = True
        try:
            unStr, uncount = self._get_username_request_string(unmax=self.max_request)
            uidStr, uidcount = self._get_user_id_request_string(uidmax=(self.max_request-uncount))
            #print uncount, ":", unStr
            #print uidcount, ":", uidStr
            if( not unStr and not uidStr ):
                self.querying = False
                return
            
            if( uncount>0 ):
                self.set_request_param(kw="screen_name",val=unStr)
            if( uidcount>0 ):
                self.set_request_param(kw="user_id",val=uidStr)

            # decide if we're doing a GET or POST
            count = uncount + uidcount
            if( count >= self.make_post_at ):
                #print "Making POST request (%d)"%(count)
                self.set_request(domain=self.get_request_domain(),
                                method="POST",
                                payload=self.get_request_params())
            else:
                #print "Making GET request (%d)"%(count)
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
                self.put_message(m=js)
            self.querying = False
        except:
            self.querying = False
            raise
        return


def dump_message(m=None, count=-1):
    print "Message dump %d:"%(count)
    #print json.dumps(m, sort_keys=True, indent=4)
    if( "errors" in m or "error" in m ):
        try:
            error = m['errors'][0]
        except:
            error = m['error']
        print "\tError %d: %s"%(error['code'],error['message'])
        return
    elif( "location" in m and m['location'] ):
        print "\tUser:", m['name'].encode('utf-8'),
        print "aka", m['screen_name'].encode('utf-8'),
        print "(%s) @ "%(str(m['id'])),m['location'].encode('utf-8')
    else:
        print "\tUser:",m['name'].encode('utf-8'),
        print "aka", m['screen_name'].encode('utf-8'),
        print "(%s)"%(str(m['id']))
    if( "description" in m and m['description'] ):
        print "\t",m['description'].encode('utf-8')
    else:
        print "\t<NO DESCRIPTION>"
    if( "status" in m and "text" in m['status'] ):
        print "\t",m['status']['text'].encode('utf-8')
    else:
        print "\t<NO STATUS MESSAGE>"
    return

    
def test_requests(p=None,twit=None):
    twit.set_post_threshold(t=8)
    twit.set_request_threshold(t=10)
    twit.start_thread()
    
    if( p['test']=="ids" or p['test']=="both" ):
        print "Adding user ids:",twit.messages()
        # 1
        twit.add_user_id(135899401) # dwmcphd
        # 2
        twit.add_user_id(2061681) # gumption
        # 3
        twit.add_user_id(48380240) # rbmllr
        # 4
        twit.add_user_id(19203768) # katestarbird
        # 5
        twit.add_user_id(208195843) # ASISTsigSI
        # 6
        twit.add_user_id(12077242) # peiyaoh
        # 7
        twit.add_user_id(270816968) # bsbutlerUMD
        # 8
        twit.add_user_id(450842550) # WikiResearch
        print "Messages waiting (ids:1):",twit.messages()
        #twit.add_user_id(14821718) # jfelipe
        #twit.add_user_id(236593313) # ynagar1
        #twit.add_user_id(5802352) # svoida
        #twit.add_user_id(16602649) # soldham
        # 9, 10, 11, 12
        twit.add_user_id([14821718,236593313,5802352,16602649])
        # jfelipe, ynagar1, svoida, soldham
        #twit.add_user_id(21094530) # wgl
        #twit.add_user_id(13318232) # katiedert
        # 13, 14
        twit.add_user_id([21094530,13318232])
        # wgl, katiedert
        print "Messages waiting (ids:2):",twit.messages()
        twit.wait_request()
        twit.start_request()
        twit.wait_request()
        print "Messages waiting (ids:3):",twit.messages()

    if( p['test']=="names" or p['test']=="both" ):
        print "Adding user names:",twit.messages()
        # 1
        twit.add_username("andabatae")
        # 2
        twit.add_username("iper")
        # 3
        twit.add_username("droffigc")
        # 4
        twit.add_username("palen")
        # 5
        twit.add_username("ineffablicious")
        # 6
        twit.add_username("bederson")
        # 7
        twit.add_username("jofish")
        # 8
        twit.add_username("noshir")
        # 9
        twit.add_username("shiladsen")
        # 10
        twit.add_username("ahnjune")
        print "Messages waiting (names:1):",twit.messages()
        # 11, 12, 13
        twit.add_username(["wylmc","sharoda","bkeegan"])
        # 14, 15, 16, 17, 18
        twit.add_username(["AaronGenest","mihaela_v","zachry","Seenivas","AndrewRaij"])
        print "Messages waiting (names:2):",twit.messages()
        twit.wait_request()
        twit.start_request()
        twit.wait_request()
        print "Messages waiting (names:3):",twit.messages()

    twit.start_request()
    twit.wait_request()
    if( twit.messages()==0 ):
        print "No results from query."
        return

    m = None
    count = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        m = twit.get_message()
        if( m ):
            #print json.dumps(m, sort_keys=True, indent=4)
            if( type(m)==list ):
                for item in m:
                    count += 1
                    if( p['json'] ):
                        print json.dumps(item, sort_keys=True, indent=4)
                    else:
                        dump_message(item,count)
            else:
                count += 1
                if( p['json'] ):
                    print json.dumps(item, sort_keys=True, indent=4)
                else:
                    dump_message(item,count)

    if( p['limits'] ):
        print "Limits:",twit.get_rate_limit(),twit._throttling()

    twit.terminate_thread()
    return


def parse_params(argv):
    uid = None
    username = None
    count = 200
    auth = None
    user = None
    test = None
    limits = False
    debug = False
    logging = False
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

        if( param == "-limits"):
            limits = True
            test = None
        if( param == "-debug"):
            debug = True
        if( param == "-json"):
            json = True
        if( param == "-log"):
            logging = True
        if( param == "-test"):
            pc += 1
            test = argv[pc].lower()
        pc += 1
    return {'auth':auth, 'user':user, 
            'test':test, 'uname':username, 'uid':uid,
            'debug':debug, 'json':json, 'logging':logging, 'limits':limits }

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> [-n <username> | -id <userid>] [-json] [-limits] [-test names|ids|both]"%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 2:
        usage(argv)

    p = parse_params(argv)
    print p

    twit = UserLookup()
    twit.set_user_agent(agent="random")
    twit.set_request_threshold(t=8)
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
        lg = Login( name="UserLookupLogin",
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

    if( p['test'] ):
        test_requests(p,twit)
        return

    if( p['uid'] ):
        print "Requesting UID:",p['uid']
        twit.add_user_id(long(p['uid']))
    elif( p['uname'] ):    
        print "Requesting user:",p['uname']
        twit.add_username(p['uname'])
    else:
        #twit.add_username('BronxZoosCobra')
        print "Must supply a user screen name or user ID."
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
        return

    m = None
    count = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        m = twit.get_message()
        if( m ):
            #print json.dumps(m, sort_keys=True, indent=4)
            if( type(m)==list ):
                for item in m:
                    count += 1
                    if( p['json'] ):
                        print json.dumps(item, sort_keys=True, indent=4)
                    else:
                        dump_message(item,count)
            else:
                count += 1
                if( p['json'] ):
                    print json.dumps(item, sort_keys=True, indent=4)
                else:
                    dump_message(item,count)

    if( p['limits'] ):
        print "Limits:",twit.get_rate_limit(),twit._throttling()

    twit.terminate_thread()
    return

if __name__ == '__main__':
    main(sys.argv)
