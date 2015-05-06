#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: dbConfig.py
#
#   A simple DB configuration object 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
class DBConfiguration(object):
    def __init__(self, 
                 protocol  = 'mysql', 
                 db_name = None,
                 host_name = None, 
                 user_name = None, 
                 password = None,
                 module_path = None,
                 db_settings = None,
                 test = False):

        if( db_settings ):
            self.db_name = db_settings['database_name']
            self.protocol = db_settings['database_protocol'].lower()
            self.host_name = db_settings['database_host']
            self.user_name = db_settings['database_user']
            self.password = db_settings['database_pass']
            self.module_path = db_settings['module_path']
        else:
            self.db_name = db_name
            self.protocol = protocol.lower()
            self.host_name = host_name
            self.user_name = user_name
            self.password = password
            self.module_path = module_path
        self.test = test


    def __repr__(self):
        result = "DBConfiguration():\n\t"
        result = result + "PROTOCOL='%s'\n\t"%(self.protocol)
        result = result + "DATABASE_NAME='%s'\n\t"%(self.db_name)
        result = result + "DATABASE_HOST='%s'\n\t"%(self.host_name)
        result = result + "DATABASE_USER='%s'\n\t"%(self.user_name)
        if( self.password ):
            result = result + "PASSWORD <is_set>\n\t"
        else:
            result = result + "PASSWORD <is_NOT_set>\n\t"
        result = result + "MODULE_PATH='%s'"%(self.module_path)
        return result


