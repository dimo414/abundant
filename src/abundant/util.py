# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
A set of utility operations used throughout Abundant.

@author: Michael Diamond
Created on Feb 7, 2011
'''

import hashlib, optparse, os
import error

def hash(text):
    '''Return a hash of the given text for use as an id.
    
    Currently SHA1 hashing is used.  It should be plenty for our purposes.'''
    return hashlib.sha1(text.encode('utf-8')).hexdigest()

def find_db(p):
    '''Identifies the issue database to work with
    
    From Mercurial cmdutil.py'''
    while not os.path.isdir(os.path.join(p, ".ab")):
        oldp, p = p, os.path.dirname(p)
        if p == oldp:
            return None

    return p

def list2str(ls):
    '''Returns a list as a pretty string'''
    if isinstance(ls,list):
        return str(ls)[1:-1]
    return ls

def diff_dict(to,fro):
    '''Identifies and returns the differences between
    two dicts as a dictionary of fields to tuples 
    where the first entry in the tuple is the to value,
    or None if the data was removed, and the second entry
    is the from value, or None if the data was added.
    
    Note that this method explicitly treats None and []
    as nonexistent for the sake of the diff.'''
    diff = {}
    def empty(dict,key):
        return dict[key] == None or dict[key] == []
    
    for key in fro.keys():
        if key not in to or empty(to,key) and not empty(fro,key):
            diff[key] = (None,fro[key])
    for key in to.keys():
        if key not in fro or empty(fro,key) and not empty(to,key):
            diff[key] = (to[key],None)
        elif to[key] != [] and fro[key] != [] and to[key] != fro[key]:
            diff[key] = (to[key],fro[key])  
    return diff 

parser_option = optparse.make_option

class _ThrowParser(optparse.OptionParser):
    def error(self, msg):
        """Overrides optparse's default error handling
        and instead raises an exception which will be caught upstream
        """
        raise optparse.OptParseError(msg)

def parse_cli(args, opts):
    '''Takes a list of arguments to the command line, and a
    data structure of options, and returns a tuple of the 
    remaining positional arguments and the options parsed
    out of the arguments
    
    Opts Structure:
    the opts structure should be a tuple of the following:
    
    '''
    # help is handled elsewhere
    parser = _ThrowParser(add_help_option=False,option_list=opts)
    
    try:
        return parser.parse_args(args)
    except optparse.OptParseError as err:
        raise error.ParsingError(err.msg)
