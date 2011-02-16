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
    
        
    