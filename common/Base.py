#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: Base.py
#
#   A base class for making asynchronous web service requests
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, gc, json, time, logging, random, copy
import requests
from requests.exceptions import HTTPError, URLRequired
from threading import Thread, Semaphore
from infx.common.AsyncTimer import AsyncTimer


class Base(Thread):
    def __init__(self, 
                 name="Base",
                 logger=None,
                 args=(),
                 kwargs={}):
        Thread.__init__(self, name=name, args=args, kwargs=kwargs)
        
        # First disable the "requests" chatty log messages, yuck
        requests_logger = logging.getLogger("requests")
        requests_logger.setLevel("ERROR")
        
        self.requests_session = None
        self.logger = None
        if( logger ):
            self.logger = logger
        else:
            fmt='[%(asctime)s][%(module)s:%(funcName)s():%(lineno)d] %(levelname)s:%(message)s'
            logging.basicConfig(format=fmt,
                                level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        self.async_timer = None
        self.msem = Semaphore(1)  # semaphore for the message buffer
        self.rsem = Semaphore(1)  # semaphore for the request activity
        self.message_queue = []
        self.pqsem = Semaphore(1) # semaphore for queue of prior requests
        self.prior_requests = []  # a queue/list of prior requests
        self.rqsem = Semaphore(1) # semaphore to prevent changes to the request_data
        self._request_data = {}  # the request_data that is to be used for the request
        self.headers = {}
        self.max_prior_requests = 25
        self.max_queue_len = 8000 # max message queue length
        self.querying = False
        self.running = False
        self.my_receiver = None
        self.request_pages = 10   # when paged, how many pages to request
        self.domain = None        # the domain, url prefix, for this request
        self.req_params = {}
        self.throttling = False
        self.last_throttle_check = None
        self.throttle_wait = 0
        self.auth_obj = None
        self.debug_output = False

        self.reset_requests_session()

    ##
    # resets the requests http sessions for this object
    #
    def reset_requests_session(self):
        if( self.requests_session ):
            self.requests_session.close()
            self.requests_session = None
            gc.collect()
        self.requests_session = requests.Session()
        r_a1 = requests.adapters.HTTPAdapter(pool_connections=100,
                                             pool_maxsize=100,
                                             max_retries=3)
        r_a2 = requests.adapters.HTTPAdapter(pool_connections=100, 
                                             pool_maxsize=100,
                                             max_retries=3)
        self.requests_session.mount('http://', r_a1)
        self.requests_session.mount('https://', r_a2)
        if( self.auth_obj ):
            self.auth_obj.reset_requests_session()
        return

    ##
    # Sets a "fake" user agent for an http request. The default is a
    # python specific script user agent. Some web services will deny
    # script based requests. 
    #
    def set_user_agent(self, agent="random"):
        if( agent ):
            if( agent=="random" ):
                agents = ['ie','mozilla','safari','opera','konqueror','chrome','android']
                agent = agents[random.randint(0,6)]
            if( agent=="mozilla" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201"
            elif( agent=="safari" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_3; en-US) AppleWebKit/535.20 (KHTML, like Gecko) Version/5.1 Safari/535.20"
            elif( agent=="chrome" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36"
            elif( agent=="opera" ):
                self.headers["User-Agent"] = "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en-US) Presto/2.9.168 Version/11.52"
            elif( agent=="konqueror" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (X11) KHTML/4.9.1 (like Gecko) Konqueror/4.9"
            elif( agent=="ie" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)"
            elif( agent=="android" ):
                self.headers["User-Agent"] = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-US; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
            else:
                if( "User-Agent" in self.headers ):
                    del self.headers["User-Agent"]
        else:
            if( "User-Agent" in self.headers ):
                del self.headers["User-Agent"]

    ##
    # Returns a copy of the http headers information
    #
    def get_request_headers(self):
        return self.headers.copy()

    ##
    # Sets the domain for an http request
    #
    def set_request_domain(self, domain=None):
        if( domain ):
            if(domain.startswith("http://") or domain.startswith("https://")):
                self.domain = domain
            else:
                self.domain = "http://"+domain
        else:
            self.domain = None

    ##
    # Get the current domain for this http request
    #
    def get_request_domain(self):
        return self.domain

    ##
    # Sets the value for an http request keyword
    #
    def set_request_param(self, kw=None, val=None):
        assert kw is not None
        if( val ):
            self.req_params[kw] = val
        else:
            if( kw in self.req_params ):
                del self.req_params[kw]

    ##
    # Removes the value for an http request keyword
    #
    def remove_request_param(self, kw=None):
        assert kw is not None
        if( kw in self.req_params ):
            del self.req_params[kw]

    ##
    # Returns a copy of the http request parameters, keys and values
    #
    def get_request_params(self):
        return self.req_params

    ##
    # Clears the http request parameters
    #
    def clear_request_params(self):
        self.req_params = {}

    ##
    # Returns the value for one http request keyword
    #
    def get_request_param(self, kw=None):
        assert kw is not None
        result = None
        if( kw in self.req_params ):
            result = self.req_params[kw]
        return result

    ##
    # This sets the request info prior to making the request, this is the
    # way to set the 
    # 
    #
    def set_request(self, domain=None, params=None, method="GET", headers=None, payload=None):
        self.rqsem.acquire()
        self._request_data = {}
        if( domain ):
            self._request_data['domain'] = domain
            self._request_data['params'] = None
            self._request_data['method'] = None
            self._request_data['headers'] = None
            self._request_data['payload'] = None
            if( params ):
                self._request_data['params'] = params
                if( params is str ):
                    self._request_data['params'] = None
                    if( params.startswith('?') or domain.endswith('?') ):
                        self._request_data['domain'] = domain+params
                    else:
                        self._request_data['domain'] = domain+"?"+params
            if( method ):
                self._request_data['method'] = method.upper()
                if( self._request_data['method']=="POST" ):
                    self._request_data['payload'] = payload
            if( headers ):
                self._request_data['headers'] = headers
            else:
                self._request_data['headers'] = self.headers
        self.rqsem.release()
        return

    ##
    # Pushes the information of the request onto the prior_requests queue
    #
    def push_request_info(self, request=None):
        self.rqsem.acquire()
        info = {}
        if( request ):
            info = copy.copy(request)
        else:
            info = copy.copy(self._request_data)
        self.rqsem.release()
        info['response'] = None
        info['warning'] = None
        info['error'] = None
        info['success'] = None        
        self.pqsem.acquire()
        if( len(self.prior_requests) < self.max_prior_requests ):
            self.prior_requests.append(info)
        else:
            # append adds to the end, this shifts the whole
            # list to the left, dropping out one item to keep
            # the total number of items in the list fixed
            self.prior_requests = self.prior_requests[1:]
            self.prior_requests.append(info)
        self.pqsem.release()
        return

    ##
    # Returns the information of the last quest from prior_requests
    #
    def get_request_info(self):
        self.pqsem.acquire()
        item = None
        if( len(self.prior_requests) > 0 ):
            # return the last item in the list,
            # but don't pop and remove it
            item = self.prior_requests[-1]
        self.pqsem.release()
        return item

    ##
    # Pops the information of the last quest from prior_requests
    #
    def pop_request_info(self):
        self.pqsem.acquire()
        item = None
        if( len(self.prior_requests) > 0 ):
            item = self.prior_requests.pop()
        self.pqsem.release()
        return item

    ##
    # Returns the number of request info items that that can be reviewed
    #
    def has_request_info(self):
        self.pqsem.acquire()
        count = len(self.prior_requests)
        self.pqsem.release()
        return count

    ##
    # Clears the prior_requests set
    #
    def clear_request_info(self):
        self.pqsem.acquire()
        self.prior_requests = []
        self.pqsem.release()

    ##
    # Looks for a specific header key in an http response header and
    # returns that value if it exists
    #
    def get_header_value(self, headers=None, key=None):
        val = None
        if( headers ):
            if( isinstance(headers,requests.structures.CaseInsensitiveDict) ):
                k = key.lower().replace(':','')
                try:
                    val = headers[k]
                except KeyError, ke:
                    val = None
            else:
                hstr = str(headers).replace("\r",'')
                hlines = hstr.split("\n")
                for line in hlines:
                    #print "\t:",line
                    if( line.startswith(key) ):
                        val = line.replace(key,'')
                        break
        return val

    ##
    # Sets the authorization object for this object, if this is
    # not set, then this is not handled as an authenticated request
    #
    def set_auth_obj(self, obj=None):
        self.auth_obj = obj
        if( self.auth_obj ):
            self.auth_obj.reset_requests_session()

    ##
    # returns the authorization object for this object
    #
    def get_auth_obj(self):
        return self.auth_obj

    ##
    # Sets the receiver for this web service data request
    # If the web service request has a receiver object then that
    # will be where the pages of the request are posted. Otherwise
    # items will be placed into the existing message queue.
    #
    def set_receiver(self, obj=None):
        self.my_receiver = obj

    ##
    # Get the receiver for this web service object
    #
    def get_receiver(self):
        return self.my_receiver

    ##
    # Sets the number of pages that will be retrieved for this web service
    # request. This is only used for a paged request. Some requests are not
    # paged - in those cases this value should be ignored.
    #
    def set_pages_to_request(self, r=25):
        self.request_pages = r

    ##
    # If this is in the process of making a query, then this is True.
    #
    def query_in_process(self):
        return self.querying

    ##
    # Status of the query thread
    #
    def is_running(self):
        return self.running

    ##
    # Sets whether or not we are going to be throttling these queries
    #
    def set_throttling(self, tr=False):
        self.throttling = tr

    ##
    # How long a wait might be
    #
    def _throttling(self, qs=None):
        waits = 0.0
        if( self.throttling ):
            if( qs<0.5 ):
                return 2.5
            elif( qs<1.0 ):
                return 1.5
            elif( qs<2.0 ):
                return 0.75
        return waits

    ##
    # Forces a wait to help throttle overly active queries. If the
    # do_wait is set to True (default) then this forces a sleep,
    # otherwise, this just returns the amount that would have been slept.
    #
    def _throttle_queries(self, do_wait=True):
        waits = 0.0
        throttle_check = time.clock()
        if( self.throttling ):
            # a one-off query will not get stopped here
            if( self.last_throttle_check ):
                diff = throttle_check-self.last_throttle_check
                waits = self._throttling(qs=diff)
                if( do_wait ):
                    time.sleep(waits)
        self.last_throttle_check = throttle_check
        return waits

    ##
    # Web service objects have a message queue. This allows
    # responses to be put into a results queue for later access.
    # A semaphore object is used to serialize access to the queue.
    #
    def put_message(self, m=None):
        if( self.my_receiver ):
            self.my_receiver.put_message(m)
        else:
            self.msem.acquire()
            #print "Base:put_message() queue_len::%d (%d)"%(len(self.message_queue),self.max_queue_len)
            if( len(self.message_queue) < self.max_queue_len ):
                self.message_queue.append(m)
            else:
                self.logger.info("Message queue length exceeded")
            self.msem.release()

    ##
    # Web service objects have a message queue. This allows other
    # objects/threads to check the number of messages in the queue.
    # A semaphore object is used to serialize access to the queue.
    #
    def messages(self):
        count = None
        self.msem.acquire()
        count = len(self.message_queue)
        self.msem.release()
        return count

    ##
    # Web service objects have a message queue. This allows other
    # objects/threads to get an item from the queue.
    # A semaphore object is used to serialize access to the queue.
    #
    def get_message(self,flush=False):
        data = None
        self.msem.acquire()
        if( len(self.message_queue) > 0 ):
            if( flush ):
                self.message_queue = []
            else:
                data = self.message_queue[0]
                self.message_queue = self.message_queue[1:]
                #print "Base:get_message() queue_len::%d (%d)"%(len(self.message_queue),self.max_queue_len)
        self.msem.release()
        return data

    ##
    # This start method is a sideways override to make sure that
    # our own self.running variable is set to True before the
    # run() method is called by the start() method in
    # multiprocessing.Process
    #
    def start_thread(self, d=True):
        self.daemon = d # Trick for this case
        self.running = True
        self.rsem.acquire()
        if( self.async_timer ):
            self.async_timer.start_thread()
        self.start()

    ##
    # This terminate is just a simple override to make sure that
    # our own self.running variable is set to False before the
    # thread is terminated.
    #
    def terminate_thread(self):
        if( self.async_timer ):
            self.async_timer.terminate_thread()
        self.running = False
        self.rsem.release()

    ##
    # Initialize an asynchronous timer that will be used to initiate
    # timed requests
    #
    def set_async_timer(self, m=0, s=10, r=0):
        n = self.name + "Timer"
        timer = AsyncTimer(name=n)
        timer.set_timer(m=m,s=s)
        if( r>0 ):
            timer.set_randomness(r=r)
        timer.set_ws_obj(obj=self)
        self.async_timer = timer

    ##
    # Trivial HTTP error handling for this object
    #
    def handle_http_error(self, err=None, wait=90):
        assert err is not None
        if err.getcode() in [300, 301, 302, 303, 304, 305, 306, 307]:
            mesg = "HTTPError %s"%(str(err.getcode()))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return False
        elif err.getcode() in [400, 401, 402, 403, 404, 408, 409, 410, 420]:
            mesg = "HTTPError %s"%(str(err.getcode()))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return False
        elif err.getcode() in [500, 501, 502, 503, 504, 505, 506, 507, 510]:
            mesg = "HTTPError %s"%(str(err.getcode()))
            self.logger.info(mesg)
            #self.logger.info(err.strerror)
            return False
        else:
            return False
        return False


    ##
    # The low-level helper function that makes an authenticated request
    #
    def _auth_request(self, request=None):
        assert request is not None
        result = []
        if( request ):
            self.push_request_info(request=request)
            result = self.auth_obj.make_request(request=request)
        return result


    ##
    # The low-level call to actually make the request. Will handle some
    # limited HTTP error conditions. The subclass should plan to write
    # a more sophisticated HTTP error handler. It is probably not
    # necessary to override _make_request. This routine should work for
    # most normal subclasses
    #
    def _make_request(self, request=None, calls=4):
        assert request is not None
        result = []
        try:
            if( self.auth_obj ):
                result = self._auth_request(request=request)
            else:
                self.push_request_info(request=request)
                if( request['method']=="POST" ):
                    result = self.requests_session.post(request['domain'],
                                                        params=request['params'],
                                                        headers=request['headers'],
                                                        data=request['payload'])
                else:
                    result = self.requests_session.get(request['domain'],
                                                       params=request['params'],
                                                       headers=request['headers'])
            #print "in Base.py _make_request()"
            #print result
            #print result.text
            if( result or result.text ):
                rinfo = self.get_request_info()
                if( rinfo ):
                    rinfo['success']=True
                    rinfo['response']=result
            if( self.throttling ):
                self._throttle_queries(do_wait=True)
        
        except requests.exceptions.HTTPError, err:
            if( calls<=0 ):
                mesg = "%d requests, HTTPError %s"%((4-calls),str(err))
                self.logger.info(mesg)
                return result
            if(self.handle_http_error(err=err)):
                mesg = "Caught HTTPError (call:%d) - %s"%((4-calls),str(err.getcode()))
                self.logger.info(mesg)
                result = self._make_request(request=request,calls=(calls-1))
            else:
                mesg = "%d requests, HTTPError %s"%((4-calls),str(err))
                self.logger.info(mesg)
                #self.logger.info(err.strerror)
                raise

        except requests.exceptions.ConnectionError, err:
            if( calls<=0 ):
                mesg = "%d requests, ConnectionError error: %s"%((4-calls),str(err))
                #print mesg
                self.logger.info(mesg)
                mesg = "BAH! - Giving up on this Connection Thread!!!"
                #print mesg
                self.logger.info(mesg)
                raise err
            else:
                mesg = "Caught ConnectionError error (call:%d) - %s"%((4-calls),str(err))
                #print mesg
                self.logger.info(mesg)
                mesg = "Resetting self.requests_session, requesting again"
                #print mesg
                self.logger.info(mesg)
                self.reset_requests_session()
                result = self._make_request(request=request,calls=(calls-1))

        except requests.exceptions.URLRequired, err:
            mesg = "Caught URLRequired error (call:%d) - %s"%((4-calls),str(err))
            self.logger.info(mesg)
            raise err
        return result
    
    ##
    # The general level request routine. This is the routine that is
    # called when this is being threaded. This is the routine that should
    # be overridden
    #
    def make_request(self):
        try:
            self.querying = True
            request_results = []
            #print "REQUEST:", self._request_data
            request_results = self._make_request(request=self._request_data)
            if( request_results ):
                try:
                    js = request_results.json()
                    self.put_message(m=js)
                except ValueError, e:
                    self.put_message(m=request_results)
            self.querying = False
        except:
            self.querying = False
            raise
        return request_results
    
    
    ##
    # This idiom is used frequently for asynchronous requests
    # The thread calling this wait, should *NOT* be called by *THIS*
    # thread or the web request will end up in a deadlock!
    #
    def wait_request(self):
        time.sleep(2)
        while( (self.messages()<1) and self.query_in_process() ):
            time.sleep(2)

    ##
    # This simply releases a semaphore lock to allow the waiting
    # thread to make the actual request. When this is being run as
    # a thread - this is the way to have the thread issue requests.
    #
    def start_request(self):
        self.rsem.release()
        return

    ##
    # This run method simply waits for the blocking semaphore to be
    # released - and then it issues the request.
    #
    def run(self):
        try:
            while( self.running ):
                self.rsem.acquire()
                self.make_request()
        except:
            self.running = False
            raise
        return
