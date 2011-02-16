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
    two dicts as a tuple of (added,removed,changed)
    where added is data in to but not in fro, removed
    is in fro but not to, and changed contains tuples
    of data in to that is different from fro.
    
    Note that this method explicitly treats None and []
    as nonexistant for the sake of the diff.
    
    To get a count of the number of changes:
    sum([len(s) for s in to.diff(fro)])'''
    added = {}
    removed = {}
    changed = {}
    def empty(dict,key):
        return dict[key] == None or dict[key] == []
    
    for key in fro.keys():
        if key not in to or empty(to,key) and not empty(fro,key):
            removed[key] = fro[key]
    for key in to.keys():
        if key not in fro or empty(fro,key) and not empty(to,key):
            added[key] = to[key]
        elif to[key] != [] and fro[key] != [] and to[key] != fro[key]:
            changed[key] = (to[key],fro[key])  
    return (added,removed,changed)  

parser_option = optparse.make_option

def parse_cli(args, opts):
    '''Takes a list of arguments to the command line, and a
    data structure of options, and returns a tuple of the 
    remaining positional arguments and the options parsed
    out of the arguments
    
    Opts Structure:
    the opts structure should be a tuple of the following:
    
    '''
    # help is handled elsewhere
    parser = optparse.OptionParser(add_help_option=False,option_list=opts)
    
    return parser.parse_args(args)
    
def issue_prefix(db):
    '''Given a database structure, return a Prefix
    object of the prefixes of the issues.
    
    This is a potentially expensive command, avoid running
    more than necessary.'''
    import issue, prefix
    list = [i.replace(issue.ext,'') for i in os.listdir(db.issues)]
    return prefix.Prefix(list)