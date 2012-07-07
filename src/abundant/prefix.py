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

This class is used in Abundant to easily access many datasets, including
issue IDs, commands, usernames, and more.

@author: Michael Diamond
Created on Feb 14, 2011
'''

import bisect
from abundant import error;

#
# A previous implementation of a prefix lookup based on a Trie:
# http://en.wikipedia.org/wiki/Trie
# was removed in favor of the current implementation, which favors
# search speed over insertion speed.  The Trie implementation was
# slower to construct, but enabled much faster insertions.
#
# Revision 49331875cb8c contains the Trie structure.
#
class Prefix:
    '''
    An prefix data structure built on a sorted list, which uses binary search.
    
    Note that for more reasonable lookup, the trie only searches in lower
    case.  This means there can be colliding strings such as 'prefix' vs 'Prefix'.
    In this case, more recent inserts override older ones.
    '''
    def __init__(self, ls=[], presorted=False):
        self._aliases = {}
        self._list = ls if presorted else sorted(ls)
        self._keys = [s.lower() for s in self._list]
    
    # Note that since we usually use these methods together, it's wasteful to
    # Compute prefix.lower() for both - as such, these methods assume prefix
    # is already lower case.
    def _getindex(self, prefix):
        return bisect.bisect_left(self._keys, prefix)
    def _getnextindex(self, prefix):
        # http://stackoverflow.com/a/7381253/113632
        lo, hi = 0, len(self._keys)
        while lo < hi:
            mid = (lo+hi)//2
            if prefix < self._keys[mid] and not self._keys[mid].startswith(prefix): hi = mid
            else: lo = mid+1
        return lo
    
    def __getitem__(self, prefix):
        '''Return the item with the given prefix.
        
        If more than one item matches the prefix an AmbiguousPrefix exception
        will be raised, unless the prefix is the entire ID of one task.
        
        If no items match the prefix an UnknownPrefix exception will be raised.
        
        If an item exactly matches the prefix, it will be returned even if
        there exist other (longer) items which match the prefix
        '''
        pre = prefix.lower()
        ret = self._list[self._getindex(pre):self._getnextindex(pre)]
        if ret:
            if len(ret) == 1 or ret[0].lower() == pre:
                return self._aliases[ret[0]] if ret[0] in self._aliases else ret[0]
            raise error.AmbiguousPrefix(prefix,ret)
        raise error.UnknownPrefix(prefix)
    
    def prefix(self, item):
        '''Return the unique prefix of the given item, or None if not found'''
        ln = len(self._keys)
        item = item.lower()
        index = self._getindex(item)
        if index >= ln:
            return None
        match = self._keys[index]
        if not match.startswith(item):
            return None
        
        siblings = []
        if index > 0:
            siblings.append(self._keys[index-1])
        if index < ln-1:
            siblings.append(self._keys[index+1])
        
        if not siblings: #list contains only item
            return match[0]
        
        return self._uniqueprefix(match,siblings)
        
    def _uniqueprefix(self,match,others):
        '''Returns the unique prefix of match, against the set of others'''
        ret = []
        #print("START:",match,others)
        while match:
            others = [s[1:] for s in others if s and s[0] == match[0]]
            ret.append(match[0])
            match = match[1:]
            #print("WHILE:",match,others,''.join(ret))
            if not others:
                return ''.join(ret)
        return None
    
    def add(self,item):
        '''Add an item to the data structure.
        
        This uses list.insert() which is O(n) - for many insertions,
        it may be dramatically faster to simply build a new Prefix entirely.'''
        lower = item.lower()
        index = self._getindex(lower)
        # If overwriting same key
        if index < len(self._keys) and self._keys[index] == lower:
            self._list[index] = item
        else:
            self._keys.insert(index,lower)
            self._list.insert(index,item)
    
    def alias(self,alias,item):
        '''Add an item to the trie which maps to another item'''
        self._aliases[alias] = self[item]
        self.add(alias)
        
    def pref_str(self,pref,short=False):
        '''returns the item with a colon indicating the shortest unique prefix'''
        item = self[pref]
        pref = self.prefix(item)
        tail = item[len(pref):]
        return item[:len(pref)]+':'+(tail[:4]+('...' if len(tail) > 4 else '') if short else tail)
    
    def __iter__(self):
        return iter(self._list)

def _test():
    p = Prefix(reversed(['a','and','hello','pi','yellow','code','contribute','hell']))
    
    print(p['a'])
    print(p['an'])
    print(p.prefix('hello'))
    p.add("howitzer")
    print(p.prefix('hello'))
    p.add('aNd')
    print(p['an'])
    p.alias('nothing','hell')
    print(p['not'])
    try:
        print(p['pie'])
    except error.UnknownPrefix as err:
        print("%s is an unkown." % err.prefix)
    try:
        print(p['co'])
    except error.AmbiguousPrefix as err:
        print("%s is ambiguous, choices: %s" % (err.prefix,err.choices))
