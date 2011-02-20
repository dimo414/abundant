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

class Prefix:
    '''
    A Trie datastructure (http://en.wikipedia.org/wiki/Trie) which enables
    fast data retrieval by prefix.  
    '''

    def __init__(self,list):
        self._root = _Node(None,True)
        for i in list:
            self._root.add(i)
    
    def __getitem__(self, prefix):
        '''Return the item with the given prefix.
        
        If more than one item matches the prefix an AmbiguousPrefix exception
        will be raised, unless the prefix is the entire ID of one task.
        
        If no items match the prefix an UnknownPrefix exception will be raised.
        
        If an item exactly matches the prefix, it will be returned even if
        there exist other (longer) items which match the prefix
        '''
        matched = self._root[prefix.lower()]
        if matched is None:
            raise error.UnknownPrefix(prefix)
        if matched.result is not None:
            return matched.result
        else:
            raise error.AmbiguousPrefix(prefix,matched.all())
    
    def prefix(self,item):
        '''Return the unique prefix of the given item, or None if not found'''
        return self._root.prefix(item)
            
    def add(self,item):
        '''Add an item to the data structure'''
        self._root.add(item,0)
        
class _Node:
    '''Represents a node in the Trie.  It contains either
    an exact match, a set of children, or both
    '''
    
    def __init__(self, item, final=False):
        '''Constructs a new node which contains an item'''
        self.final = final
        self.result = item
        self.children = {}
    
    def _tree(self):
        return "( %s%s, { %s } )" % (self.result, '*' if self.final else '',
                                   ', '.join(["%s: %s" % (k,v._tree()) for (k,v) in self.children.items()]))
    
    def add(self,item,depth=0):
        if self.result is not None and not self.final:
            print(self.result,item,depth)
            res_letter = self.result[depth].lower()
            self.children[res_letter] = _Node(self.result,len(self.result)==depth+1)
            self.result = None
            
        if len(item) == depth:
            self.result = item #this could override an old value
            self.final = True
            return
        
        letter = item[depth].lower()
        if letter in self.children:
            child = self.children[letter]
            child.add(item,depth+1)
        else:
            self.children[letter] = _Node(item,len(item) == depth+1)

    def __getitem__(self,prefix):
        if len(prefix) == 0 or len(self.children) == 0:
            return self
        letter = prefix[0]
        if letter in self.children:
            return self.children[letter][prefix[1:]]
        else: return None

    def prefix(self,item):
        if len(item) == 0 or len(self.children) == 0:
            return ''
        letter = item[0]
        if letter in self.children:
            child = self.children[letter].prefix(item[1:])
            if child is not None:
                return letter + child 
        return None
    
    def all(self):
        ret = [self.result] if self.result is not None else []
        for (_,k) in self.children.items():
            ret.extend(k.all())
        return ret
    
if __name__ == '__main__':
    p = Prefix(reversed(['a','and','hello','yellow','code','contribute','hell']))
    
    try:
        print(p['a'])
        print(p['an'])
        print(p['hel'])
        print(p.prefix('hello'))
        p.add("howitzer")
        print(p.prefix('hello'))
        print(p['co'])
    except error.AmbiguousPrefix as err:
        print("%s is ambiguous, choices: %s" % (err.prefix,err.choices))
    print(p._root._tree())