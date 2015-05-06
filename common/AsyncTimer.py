#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: AsyncTimer.py
#   DATE: April, 2012
#
#   A timer that will automatically launch timed queries for
#   asynchronous web service queries based on Base. The timer
#   will support some randomness 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, time, random
from threading import Thread

class AsyncTimer(Thread):
    def __init__(self, 
                 name="AsyncTimer",
                 args=(),
                 kwargs={}):
        Thread.__init__(self, name=name, args=args, kwargs=kwargs)
        self.ticks = 0
        self.secs = 0.0
        self.mins = 0.0
        self.randsecs = 0
        self.ws_obj = None
        self.do_print = False

    ##
    #
    def set_do_print(self, p=True):
        self.do_print = p

    ##
    #
    def set_randomness(self, r=0):
        tot = float(60.0*self.mins)+float(self.secs)
        maxrandsecs = int(tot)
        if( r>=0 ):
            if( r<=maxrandsecs ):
                self.randsecs=r
            else:
                self.randsecs=0
        else:
            self.randsecs=0

    ##
    #
    def set_timer(self, m=0.0, s=10.0):
        if( s >= 0.0 ):
            self.secs=s
        else:
            self.secs=10.0
        if( m >= 0.0 ):
            self.mins=m
        else:
            self.mins=0.0

    ##
    #
    def set_ws_obj(self, obj=None):
        self.ws_obj=obj

    ##
    #
    def run(self):
        t = float(60.0*self.mins)+float(self.secs)
        while( self.running ):
            # should there be some randomness in the timer
            if( self.randsecs > 0 ):
                sign = random.randint(0,1)
                if( sign > 0 ):
                    d = -1.0*random.randint(0,self.randsecs)
                    #print "decrease",d
                else:
                    d = random.randint(0,self.randsecs)
                    #print "increase",d
                wt = t+d
            else:
                wt = t   
            # if there is a web service request object
            if( self.ws_obj ):
                # and if the web service object is running
                if( self.ws_obj.is_running() ):
                    # make the request and then sleep
                    self.ws_obj.start_request()
                    if( self.do_print ):
                        print "<%s-%d:%f> made request"%(self.name,self.ticks,wt),
                        print self.ws_obj
                    time.sleep(wt)
                    self.ticks += 1
                else:
                    # if there is a web service objec and it's
                    # not yet running, sleep a small amount to
                    # watch for it to start running
                    time.sleep(5)
            else:
                time.sleep(wt)
                self.ticks += 1
                if( self.do_print ):
                    print "<%s-%d:%f>"%(self.name,self.ticks,wt)
        return

    ##
    #
    def start_thread(self, d=True):
        self.daemon = d
        self.running = True
        self.start()

    ##
    #
    def terminate_thread(self):
        self.running = False

def main(argv):
    timer = wAsyncTimer(name="testTimer")
    timer.set_timer(m=0,s=5)
    timer.set_randomness(r=3)
    timer.set_do_print()
    #timer.startThread(d=True)
    #time.sleep(6000)
    timer.start_thread(d=False)
    return

if __name__ == '__main__':
    main(sys.argv)   
