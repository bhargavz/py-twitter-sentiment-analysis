#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: settings_db.py
#   DATE: 2/20/2014
#   Author: Bhargav Shah
#
#   Simple database settings - for Sochi Data
#
##
# DATABASE SETTINGS
# These variables allow setting the host, protocol, username and password for
# accessing the database. If these are not set here then they should be passed
# as parameters when instantiating the DB objects.
#
DATABASE_SETTINGS = {
    ## localhost sochi collection
    'default': {
        'database_name':"tweet_infx547",
        'database_protocol':"mysql",
        'database_host':"127.0.0.1",
        'database_user':"root",
        'database_pass':"batz",
        'module_path':None
    },
    ## localhost sochi collection
    'main_db': {
        'database_name':"tweet_infx547",
        'database_protocol':"mysql",
        'database_host':"127.0.0.1",
        'database_user':"root",
        'database_pass':"batz",
        'module_path':None
    }
}
