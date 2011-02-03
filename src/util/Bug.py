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

class Bug:
    '''
    classdocs
    '''

    def __init__(self,s,hello="Hello world!"):
        '''
        Constructor
        '''
        self.s = s
        self.hello = hello
    def __repr__(self):
        return '<Bug(%s,%s)>' % (self.s, self.hello)

def bugToJSON(bug):
    return bug.__dict__

def jSONToBug(json):
    print(json)
    args = dict( (key.encode('ascii'), value) for key, value in json.items())
    print(args)
    return Bug(**args)
    
if __name__ == '__main__':
    str = json.dumps(Bug("Text",{"a":"aaaa","b":"BBBBB","C":"ccccc"}), default=bugToJSON, sort_keys=True)
    print(str)
    print(json.loads(str,object_hook=jSONToBug))
    
    