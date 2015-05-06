#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleUserMetaObj.py
#   An object that mirrors the user meta data table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.userMetaObj import userMetaObj
from datetime import datetime
import copy

class ExampleUserMetaObj(userMetaObj):

    def __init__(self):
        userMetaObj.__init__(self)

    def __repr__(self):
        result = "ExampleUserMetaObj():\n\t"
        result = result+"rid: %s\n\t"%(str(self.rid))
        result = result+"user_name: %s\n\t"%(str(self.user_name))
        result = result+"screen_name: "+self.screen_name.encode('utf-8')+"\n\t"
        result = result+"user_id: %s\n\t"%(str(self.user_id))
        result = result+"friend_count: %d\n\t"%(self.friend_count)
        result = result+"friend_collect_dt: %s\n\t"%(str(self.friend_collect_dt))
        result = result+"friend_collect_resp: %s\n\t"%(self.friend_collect_resp)
        result = result+"follower_count: %d\n\t"%(self.follower_count)
        result = result+"friend_collect_dt: %s\n\t"%(str(self.follower_collect_dt))
        result = result+"follower_collect_resp: %s"%(self.follower_collect_resp)
        return result

