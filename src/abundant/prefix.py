# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
This class represents a mapping of unique prefixes to strings.  It is given
a list of strings, and constructs a mapping such that any string which
uniquely maps to the front of a string returns the matched string.

This class is currently used in Abundant both for issue IDs and commands,
both of which the user can specify via unique prefix.

Much of this code comes from b and/or t, the Mercurial extension bug tracker
Michael Diamond built, and the task manager Steve Losh built respectively.

@author: Michael Diamond
Created on Feb 14, 2011
'''

import error;

def _prefixes(ids):
    """Return a mapping of ids to prefixes in O(n) time.
    
    Each prefix will be the shortest possible substring of the ID that
    can uniquely identify it among the given group of IDs.
    
    If an ID of one task is entirely a substring of another task's ID, the
    entire ID will be the prefix.
    
    From b
    """
    pre = {}
    for id in ids:
        id_len = len(id)
        for i in range(1, id_len+1):
            """ identifies an empty prefix slot, or a singular collision """
            prefix = id[:i]
            if (not prefix in pre) or (pre[prefix] != ':' and prefix != pre[prefix]):
                break
        if prefix in pre:
            """ if there is a collision """
            collide = pre[prefix]
            for j in range(i,id_len+1):
                if collide[:j] == id[:j]:
                    pre[id[:j]] = ':'
                else:
                    pre[collide[:j]] = collide
                    pre[id[:j]] = id
                    break
            else:
                pre[collide[:id_len+1]] = collide
                pre[id] = id
        else:
            """ no collision, can safely add """
            pre[prefix] = id
    pre = dict(zip(pre.values(),pre.keys()))
    if ':' in pre:
        del pre[':']
    return pre

class Prefix(dict):
    '''
    A custom dictionary data structure which looks up items in a list
    by unique prefixes to that item.
    '''


    def __init__(self,list):
        '''
        Takes a lit of strings to construct a map from
        '''
        self.list = list
        self._prefixes = None
    
    def __getitem__(self, prefix):
        '''Return the task with the given prefix.
        
        If more than one task matches the prefix an AmbiguousPrefix exception
        will be raised, unless the prefix is the entire ID of one task.
        
        If no tasks match the prefix an UnknownPrefix exception will be raised.
        
        From b (from t)
        '''
        matched = [item for item in self.list if item.startswith(prefix)]
        if len(matched) == 1:
            return matched[0]
        elif len(matched) == 0:
            raise error.UnknownPrefix(prefix)
        else:
            exactMatch = [item for item in self.list if item == prefix]
            if len(exactMatch) == 1:
                return exactMatch[0]
            else:
                raise error.AmbiguousPrefix(prefix,matched)
    
    def prefix(self,item):
        if self._prefixes == None:
            self._prefixes = _prefixes(self.list)
        return self._prefixes.get(item)
    
    def add(self,*items):
        self.list.extend(items)
        # this is currently less efficient than it could be
        # since we recompute all the prefixes, rather than
        # just updating conflicts.  It'd be good to improve.
        if self._prefixes != None:
            self._prefixes = _prefixes(self.list)
                        
if __name__ == '__main__':
    p = Prefix(['a','aaab','hello','yellow','code','contribute'])
    print(p['h'])
    print(p.prefix("code"))