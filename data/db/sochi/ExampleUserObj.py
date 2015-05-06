#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleUserObj.py
#
#   An object that mirrors the user data table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.userObj import userObj
from datetime import datetime
import copy

class ExampleUserObj(userObj):
    def __init__(self):
        userObj.__init__(self)

    def __repr__(self):
        result = "ExampleUserObj():\n\t"
        result = result+"rid: %s\n\t"%(str(self.rid))
        result = result+"user_name: %s\n\t"%(str(self.user_name))
        result = result+"screen_name: "+self.screen_name.encode('utf-8')+"\n\t"
        result = result+"join_dt: %s\n\t"%(str(self.join_dt))
        result = result+"user_id: %d\n\t"%(self.user_id)
        result = result+"description: "+self.description.encode('utf-8')
        return result
