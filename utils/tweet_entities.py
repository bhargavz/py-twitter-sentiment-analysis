#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: tweet_entities.py
#
#   Small rountines to process tweet entities
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import re
URL_PATTERN = re.compile(r'(http://\S*)',re.I|re.M|re.U)
RETWEET_PATTERN = re.compile(r'(rt\s*@\S*|via\s*@\S*)',re.I|re.M|re.U)
RETWEET_USER_PATTERN = re.compile(r'rt\s*@(\S*)|via\s*@(\S*)',re.I|re.M|re.U)
HASH_PATTERN = re.compile(r'(#\S*#|#\S*|\S*#)',re.I|re.M|re.U)
HASH_REPLACE_PATTERN = re.compile(r'[.,;:!?]',re.I|re.M|re.U)
MENTION_PATTERN = re.compile(r'(@\S*)',re.I|re.M|re.U)
#UNAME_REPLACE_PATTERN = re.compile(r'.,;:',re.I|re.M|re.U)



def tweet_entities(tweet_text=None, thresh=10):
    result = {'is_retweet':False,
              'is_short':False,
              'is_whitespace':False,
              'retweet_prefix':None,
              'hashes':[],
              'mentions':[],
              'urls':[],
              'guessed_retweet_from_user_name':None,
              'fixed_tweet_text':None}
    
    #print "START", tweet_text.encode('utf-8')
    matched_rts = RETWEET_PATTERN.findall(tweet_text)
    if( matched_rts ):
        result['is_retweet'] = True
        for item in matched_rts:
            result['retweet_prefix'] = item
            tweet_text = tweet_text.replace(item,'')
            matched_users = RETWEET_USER_PATTERN.match(item)
            #print "MATCHED:", matched_users
            if( matched_users and 
                (matched_users.group(1) or matched_users.group(2)) ):
                for user in matched_users.group(1,2):
                    if( user ):
                        #print "RT USER:",user.encode('utf-8')
                        #from_user = UNAME_REPLACE_PATTERN.sub('',user)
                        from_user = user.replace(':','')
                        from_user = from_user.replace(';','')
                        from_user = from_user.replace(',','')
                        from_user = from_user.replace('.','')
                        #result['guessed_retweet_from_user_name'] = user
                        result['guessed_retweet_from_user_name'] = from_user
                            

    matched_urls = URL_PATTERN.findall(tweet_text)
    if( matched_urls ):
        for item in matched_urls:
            result['urls'].append(item)
            tweet_text = tweet_text.replace(item,'')
    
    matched_hashes = HASH_PATTERN.findall(tweet_text)
    if( matched_hashes ):
        for item in matched_hashes:
            hashtag = HASH_REPLACE_PATTERN.sub('',item)
            result['hashes'].append(hashtag)
            tweet_text = tweet_text.replace(item,'')
        
    matched_mentions = MENTION_PATTERN.findall(tweet_text)
    if( matched_mentions ):
        for item in matched_mentions:
            result['mentions'].append(item)
            tweet_text = tweet_text.replace(item,'')

    tweet_text = tweet_text.strip()
    result['fixed_tweet_text'] = tweet_text
    if( len(tweet_text)<thresh ):
        result['is_short'] = True
    if( (len(tweet_text)>0) and tweet_text.isspace() ):
        result['is_whitespace'] = True
    #print "FINISH",tweet_text.encode('utf-8')
    #print result
    return result


if __name__ == '__main__':
    print "No main()"
