#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: BaseDB.py
#   DATE: April, 2012
#   The base level DB class for tweet collection and analysis
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
import os
from sqlalchemy.orm import clear_mappers

class BaseDB(object):
    def __init__(self, config = None):
        self.config = config
        self.db = None
        self.session = None
        self.limit_size = 5000
        self.offset = 0
        self.paged_qid = 1000
        self.paged_queries = { }
        

    def close(self):
        if( self.session ):
            self.session.flush()
        if( self.db ): 
            self.db.close()

    def insert_in_table(self, table, set):
        try:
            table.insert().execute(set)
        except Exception, e:
            print "FATAL ERROR while inserting recs into \"%s\" Table"(table.name)
            sys.exit(0)
        return True

    def new_paged_query(self, query):
        qid = self.paged_qid
        self.paged_qid += 1
        q_rec = {'active_query':query,'limit_size':self.limit_size,'offset':self.offset}
        self.paged_queries[qid] = q_rec
        return qid

    def get_paged_query(self, qid):
        if( self.paged_queries.has_key(qid) ):
            q_rec = self.paged_queries[qid]
            return q_rec['active_query']
        return None

    def update_paged_query(self, qid, q):
        if( self.paged_queries.has_key(qid) ):
            q_rec = self.paged_queries[qid]
            q_rec['active_query'] = q
            return True
        return False

    def delete_paged_query(self, qid):
        if( self.paged_queries.has_key(qid) ):
            del self.paged_queries[qid]
            return True
        return False

    def paged_query_page_size(self, qid, page_size):
        if( self.paged_queries.has_key(qid) ):
            q_rec = self.paged_queries[qid]
            q_rec['limit_size'] = page_size
            return True
        return False

    def paged_query_starting_offset(self, qid, s_offset):
        if( self.paged_queries.has_key(qid) ):
            q_rec = self.paged_queries[qid]
            q_rec['offset'] = s_offset
            return True
        return False

    def paged_query_next_page(self, qid):
        if( self.paged_queries.has_key(qid) ):
            q_rec = self.paged_queries[qid]
            query = q_rec['active_query']
            l = q_rec['limit_size']
            o = q_rec['offset']
            q_rec['offset'] = o + l
            return query.limit(l).offset(o)
        return None

    def delete_item(self, item):
        if( self.session ):
            self.session.delete(item)
            return True
        else:
            return False

    def update_item(self, item):
        if( self.session ):
            self.session.flush()
            return True
        else:
            return False

    def insert_item(self, item):
        if( self.session ):
            self.session.add(item)
            return True
        else:
            return False

    def commit_changes(self):
        if( self.session ):
            self.session.flush()
            return True
        else:
            return False
