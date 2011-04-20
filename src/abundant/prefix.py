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

from abundant import error;

class Prefix:
    '''
    A trie datastructure (http://en.wikipedia.org/wiki/Trie) which enables
    fast data retrieval by prefix.
    
    Note that for more reasonable lookup, the trie only searches in lower
    case.  This means there can be colliding strings such as 'prefix' vs 'Prefix'.
    In this case, more recent inserts override older ones. 
    '''

    def __init__(self,list=[]):
        self._root = _Node(None,None,True)
        self._aliases = {}
        for i in list:
            self._root.add(i.lower(),i)
    
    def __getitem__(self, prefix):
        '''Return the item with the given prefix.
        
        If more than one item matches the prefix an AmbiguousPrefix exception
        will be raised, unless the prefix is the entire ID of one task.
        
        If no items match the prefix an UnknownPrefix exception will be raised.
        
        If an item exactly matches the prefix, it will be returned even if
        there exist other (longer) items which match the prefix
        '''
        matched = self._root[prefix.lower()]
        if (matched is None or
            (matched.result is None and len(matched.children) == 0) or
            # this is needed because prefix will return if prefix
            # is longer than necessary, and the necessary part
            # matches, but the extra text does not
            (matched.key is not None and not matched.key.startswith(prefix.lower()))):
            raise error.UnknownPrefix(prefix)
        if matched.result is not None:
            if matched.result in self._aliases:
                return self._aliases[matched.result]
            else: return matched.result
        else:
            raise error.AmbiguousPrefix(prefix,matched.all())
    
    def prefix(self,item):
        '''Return the unique prefix of the given item, or None if not found'''
        return self._root.prefix(item.lower())
    
    def pref_str(self,pref,short=False):
        '''returns the item with a colon indicating the shortest unique prefix'''
        id = self[pref]
        pref = self.prefix(id)
        tail = id[len(pref):]
        return id[:len(pref)]+':'+(tail[:4]+('...' if len(tail) > 4 else '') if short else tail)
            
    def add(self,item):
        '''Add an item to the data structure'''
        self._root.add(item.lower(),item,0)
    
    def alias(self,alias,item):
        '''Add an item to the trie which maps to another item'''
        self._aliases[alias] = self[item]
        self.add(alias)
        
class _Node:
    '''Represents a node in the Trie.  It contains either
    an exact match, a set of children, or both
    '''
    
    def __init__(self, key, item, final=False):
        '''Constructs a new node which contains an item'''
        self.final = final
        self.key = key
        self.result = item
        self.children = {}
    
    def _tree(self):
        '''Returns a tree structure representing the trie.  Useful for debugging'''
        return "( %s%s, { %s } )" % (self.result, '*' if self.final else '',
                                   ', '.join(["%s: %s" % (k,v._tree()) for (k,v) in self.children.items()]))
    
    def add(self,key,item,depth=0):
        '''Adds an item at this node or deeper.  Depth indicates
        which index is being used for comparison'''
        # the correct node has been found, replace result with new value
        if self.key is not None and key == self.key:
            self.result = item #this would override an old value
            return
        
        # this is currently a leaf node, move the leave one down
        if self.result is not None and not self.final:
            if self.key == None: print(self.key,self.result,key,item)
            key_letter = self.key[depth]
            self.children[key_letter] = _Node(self.key,self.result,len(self.key)==depth+1)
            self.key = None
            self.result = None
            
        if len(item) == depth:
            self.key = key
            self.result = item #this could override an old value
            self.final = True
            return
        
        letter = key[depth]
        if letter in self.children:
            child = self.children[letter]
            child.add(key,item,depth+1)
        else:
            self.children[letter] = _Node(key,item,len(key) == depth+1)

    def __getitem__(self,prefix):
        '''Given a prefix, returns the node that matches
        This will either have a result, or if not the prefix
        was ambiguous.  If None is returned, there was no
        such prefix'''
        if len(prefix) == 0 or len(self.children) == 0:
            return self
        letter = prefix[0]
        if letter in self.children:
            return self.children[letter][prefix[1:]]
        else: return None

    def prefix(self,item):
        '''Given an item (or a prefix) finds the shortest
        prefix necessary to reach the given item.
        None if item does not exist.'''
        if len(item) == 0 or len(self.children) == 0:
            return ''
        letter = item[0]
        if letter in self.children:
            child = self.children[letter].prefix(item[1:])
            if child is not None:
                return letter + child 
        return None
    
    def all(self):
        '''Returns a list of all items in and below this node'''
        ret = [self.result] if self.result is not None else []
        for k,v in self.children.items():
            ret.extend(v.all())
        return ret
    
if __name__ == '__main__':
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
    print(p._root._tree())