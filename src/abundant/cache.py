# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
Classes, methods, and decorators to enable data-caching behavior and
minimize program execution time. 

@author: Michael Diamond
Created on June 14, 2012
'''

import functools
from abundant import util

class lazy_property(object):
    '''Decorator: Enables the value of a property to be lazy-loaded.
    From Mercurial's util.propertycache
    
    Apply this decorator to a no-argument method of a class and you
    will be able to access the result as a lazy-loaded class property.
    The method becomes inaccessible, and the property isn't loaded
    until the first time it's called.  Repeated calls to the property
    don't re-run the function.
    
    This takes advantage of the override behavior of Descriptors - 
    __get__ is only called if an attribute with the same name does
    not exist.  By not setting __set__ this is a non-data descriptor,
    and "If an instance's dictionary has an entry with the same name
    as a non-data descriptor, the dictionary entry takes precedence."
     - http://users.rcn.com/python/download/Descriptor.htm
    
    To trigger a re-computation, 'del' the property - the value, not
    this class, will be deleted, and the value will be restored upon
    the next attempt to access the property.
    '''
    def __init__(self,func):
        self.func = func
        self.name = func.__name__
    def __get__(self, obj, type=None):
        result = self.func(obj)
        setattr(obj, self.name, result)
        return result

class lazy_dict(object):
    '''Decorator: Enables a dictionary property to be lazy-loaded,
    in a similar fashion to lazy_property.
    
    Apply this decorator to a method which takes hashable arguments,
    and use the name as a dictionary in external code.  Repeated
    calls to the same index will not be recomputed.
    
    Exceptions raised by the decorated function will be wrapped as
    KeyErrors and raised.
    '''
    def __init__(self,func):
        self.orig_func = func
        self.func = func
        self.cache = {}
    
    def __get__(self, obj, objtype):
        '''Necessary to pass 'self' down to methods - not called for functions'''
        self.func = functools.partial(self.orig_func,obj)
        return self
    
    def __getitem__(self,*key):
        try:
            return self.cache[key]
        except KeyError: # Value not loaded yet
            try:
                value = self.func(*key)
            except Exception as e:
                raise KeyError("Invalid arguments '%s' for %s" % (util.list2str(key),self.orig_func.__name__)) from e
            self.cache[key] = value
            return value
        # a TypeError will be raised if passed a non-hashable argument
    
    def __setitem__(self,*key,value):
        '''Set is provided for convenience, it should be avoided - this
        dict is backed by a function, breaking that contract isn't advisable.
        '''
        self.cache[key] = value
    
    def __delitem__(self,*key):
        '''Clears the given value, re-accessing it recalls the function'''
        del self.cache[key]
    
    def __iter__(self):
        raise NotImplementedError("Unable to iter over lazy-loaded dictionary")
    
    def __contains__(self):
        raise NotImplementedError("Unable to do contains checks on lazy-loaded dictionary")