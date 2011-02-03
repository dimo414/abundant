# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''

@author: Michael Diamond
Created on Feb 2, 2011
'''

import json

class Bug(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    
if __name__ == '__main__':
    print(json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}], sort_keys=True, indent=1))