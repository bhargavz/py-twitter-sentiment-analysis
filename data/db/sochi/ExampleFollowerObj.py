#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleFollowerObj.py
#
#   An object that mirrors the followers table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.followerObj import followerObj
import copy

class ExampleFollowerObj(followerObj):
    def __init__(self):
        followerObj.__init__(self)

    def __repr__(self):
        result = "ExampleFollowerObj():\n\t"
        result = result+"rid: %s\n\t"%(str(self.rid))
        result = result+"user: "+self.user.encode('utf-8')+"\n\t"
        result = result+"follower: "+self.follower.encode('utf-8')+"\n\t"
        result = result+"user_id: %s\n\t"%(str(self.user_id))
        result = result+"follower_id: %s"%(str(self.follower_id))
        return result
