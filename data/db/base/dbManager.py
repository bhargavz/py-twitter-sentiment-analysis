#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: DBManager.py
#
#   The base level DB manager class 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.engine import reflection
from sochi.data.db.base.dbConfig import DBConfiguration
from fnmatch import fnmatch
import os

## needs to be in the global scope
session_base = sessionmaker()

class DBManager(object):
    def __init__(self, 
                 db_name = '',
                 host_name = '',
                 protocol = '',
                 user_name = '',
                 password = '',
                 module_path = '',
                 config = None):

        if( config ):
            self.config = config
        else:
            self.config = DBConfiguration(protocol = protocol,
                                          db_name = db_name,
                                          host_name = host_name, 
                                          user_name = user_name,
                                          password = password,
                                          module_path = module_path)
        self.open()
        #self.tables_to_map = [f[:-3] for f in os.listdir(module_path) if fnmatch(f,'*.py') and f!='__init__.py']
        return


    def reflect(self, clear = True, recurse = True, only = None):
        try:
            if clear:
                self.metadata.clear()
            
            self.metadata.reflect(bind = self.engine, only = only)
        except:            
            if recurse:
                self.close()
                self.open()
                self.reflect(clear = False, recurse = False, only = only)
            else:
                raise



    def open(self):
        if self.config.protocol != 'sqlite':
            args = {'use_unicode':True, 'host':self.config.host_name}
        else:
            args = {}
        connection_str = self.get_connection_string()
        #print connection_str
        self.engine = create_engine(connection_str, 
                                    connect_args=args)
        self.metadata = MetaData(bind=self.engine)
        self.session = session_base(bind=self.engine)
        self.inspector = reflection.Inspector.from_engine(self.engine)
        #self.reflect(clear = False, recurse = False)



    def close(self):
        try:
            self.metadata.clear()
            self.engine.connection_provider._pool.dispose()
            self.engine.dispose()
            del self.engine
            del self.metadata
        except:
            pass


    def get_connection_string(self):
        con = '%s://'%self.config.protocol
        if self.config.protocol != 'sqlite':
            if self.config.user_name:
                con += '%s'%self.config.user_name
                if self.config.password:
                    con += ':%s'%self.config.password
                con += '@%s'%self.config.host_name
            else:
                con += '%s'%self.config.host_name
            con += '/%s'%self.config.db_name
            # print "FIXME: db_manager.py line 78 mysql.sock setting"
            # con += '?unix_socket=/var/mysql/mysql.sock'
            # print "Setup connection to be utf8 compliant"
            # see http://www.sqlalchemy.org/docs/05/reference/dialects/mysql.html
            con += '?charset=utf8&use_unicode=0'
        else:
            con += '//%s'%self.config.db_name #assumes absolute path to sqlite db file
        
        return con



    def get_table(self, table_name):
        try:
            self.reflect(clear = False, only = [table_name])
        except Exception, e: 
            print 'could not reflect table %s : %s' % (table_name, e)
            raise e
            #print 'could not reflect table %s'%table_name
        if table_name not in self.metadata.tables:
            raise 'cannot find table %s'%table_name

        return self.metadata.tables[table_name]



    def execute(self, query, recurse = True):
        try:
            return self.engine.execute(query)
        except:
            if recurse:
                self.close()
                self.open()
                self.execute(query, recurse = False)
            else:
                raise

