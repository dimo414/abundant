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

    def __init__(self, id=None, parent=None, children=[],
                 duplicates=None, creator=None,assigned_to=None,
                 listeners=[],target=None,severity=None,status=None,
                 category=None,paths=[],description="",reproduction=
                 None,expected=None,comments=[]):
        '''
        Constructor
        '''
        self.id=id
        self.parent=parent
        self.children=children
        self.duplicates=duplicates
        self.creator=creator
        self.assigned_to=assigned_to
        self.listeners=listeners
        self.target=target
        self.severity=severity
        self.status=status
        self.category=category
        self.paths=paths
        self.description=description
        self.reproduction=reproduction
        self.expected=expected
        self.comments=comments
        
    def __repr__(self):
        return '<Bug(%s,%s)>' % (self.id, self.description)
    
    def to_JSON(self, path, file=None):
        if file == None:
            file = self.id+".bug"
        json.dump(self.__dict__,open(path+file,'w'),
                  indent=1,sort_keys=True)
    
def JSON_to_Bug(file):
    return Bug(**json.load(open(file)))

if __name__ == '__main__':
    #bug = JSON_to_Bug("s.bug")
    #print(bug)
    bug = Bug("s")
    bug.to_JSON("./")
    
    