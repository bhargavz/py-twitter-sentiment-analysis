#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: ExampleFriendObj.py
#
#   An object that mirrors the friends table in the database 
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
#
from sochi.data.db.base.friendObj import friendObj
import copy

class ExampleFriendObj(friendObj):
    def __init__(self):
        friendObj.__init__(self)

    def __repr__(self):
        result = "ExampleFriendObj():\n\t"
        result = result+"rid: %s\n\t"%(str(self.rid))
        result = result+"user: "+self.user.encode('utf-8')+"\n\t"
        result = result+"friend: "+self.friend.encode('utf-8')+"\n\t"
        result = result+"user_id: %s\n\t"%(str(self.user_id))
        result = result+"friend_id: %s"%(str(self.friend_id))
        return result
