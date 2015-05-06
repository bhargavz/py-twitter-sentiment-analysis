#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: explore_sentiment.py
#   DATE: February, 2014
#   Simple example of building a sentiment classifier
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, csv, nltk
from sochi.utils.stop_words import remove_stops, STOPLIST
from sochi.data.db.base.dbConfig import DBConfiguration
from sochi.data.db.sochi.settings_db import *
from sochi.data.db.sochi.ExampleTweetsDB import ExampleTweetsDB as DB
from sochi.data.db.sochi.ExampleTweetObj import ExampleTweetObj
from sochi.data.sochi.constants import *
from datetime import datetime, timedelta



class Sentiment(object):
    def __init__(self):
        self.complete_token_list = []
        self.training_data = None
        self.classifier = None
    
    # Load a CSV file
    def load_csv_label_data(self,fname=""):
        label_data = []
        if( fname ):
            lines = 0
            pos_examples = 0
            neg_examples = 0
            unknown = 0
            f = open(fname,"r")
            reader = csv.DictReader(f,dialect="excel")
            rec = reader.next()
            while rec:
                lines += 1
                tweet_text = rec["tweet_text"].decode('utf-8')
                clean_tweet = remove_stops(tweet_text)
                token_list = clean_tweet.split()
                if( (rec['label']=="+") or (rec['label']=="pos") or (rec['label']=="positive") ):
                    #tup = tuple(token_list,"positive")
                    tup = (token_list,"positive")
                    self.complete_token_list.extend(token_list)
                    pos_examples += 1
                elif( (rec['label']=="-") or (rec['label']=="neg") or (rec['label']=="negative") ):
                    #tup = tuple(token_list,"negative")
                    tup = (token_list,"negative")
                    self.complete_token_list.extend(token_list)
                    neg_examples += 1
                else:
                    # this one is neutral or not labeled
                    unknown += 1
                label_data.append(tup)
                try:
                    rec = reader.next()
                except:
                    rec = None
            f.close()
        return [label_data,lines,pos_examples,neg_examples,unknown]
    
    
    def features(self, doc):
        feature_dict = {}
        for tok in self.complete_token_list:
            feature_dict[tok] = (tok in doc)
        return feature_dict
    
    
    def new_classifier(self, label_data=None):
        self.training_data = nltk.classify.apply_features(self.features,label_data)
        #self.classifier = nltk.classify.naivebayes.NaiveBayesClassifier.train(self.training_data)
        self.classifier = nltk.NaiveBayesClassifier.train(self.training_data)
        return 
    
    def top_n_features(self, n=10):
        self.classifier.show_most_informative_features(n=n)
    
    def score(self, text):
        return self.classifier.classify(self.features(text))



def query_date(db=None, date=None, dur=1, by_hour=False):
    result_list = []
    if( by_hour ):
        delta = timedelta(hours=1)
    else:
        delta = timedelta(days=1)
    dt2 = date + (dur*delta)
    start_date = date.strftime("%Y%m%d%H%M%S")
    end_date = dt2.strftime("%Y%m%d%H%M%S")
    #start_date = date.strftime("%Y%m%d000000")
    #end_date = dt2.strftime("%Y%m%d000000")
    try:
        result_list = db.query_tweet_table_by_date_range(start_date=start_date,
                                                         end_date=end_date,
                                                         in_order=True)
    except Exception, e:
        print "EXCEPTION when running query!"
        print e
        result_list = []
    return {'tweet_list':result_list, 
            'query_date':date, 
            'start_date_str':start_date, 
            'end_date_str':end_date,
            'duration':dur}



def score_tweets(sent=None,tweet_list=None):
    for tweet in tweet_list:
        score = sent.score(tweet.tweet_text)
        print "%s:"%score,tweet.tweet_text.encode('utf-8')


config = DBConfiguration(db_settings=DATABASE_SETTINGS['default'])
db = DB(config=config)
dt = datetime.strptime("20140227000000","%Y%m%d%H%M%S")
day_hr0 = query_date(db=db, date=dt, dur=1, by_hour=True)


s = Sentiment()
result = s.load_csv_label_data(fname="training.csv")
s.new_classifier(label_data=result[0])
s.top_n_features(n=30)

score_tweets(sent=s,tweet_list=day_hr0['tweet_list'])

