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

import json,os,time

import util

class Issue:
    '''
    This class represents the Issue data structure, and notably is responsible
    for serializing and unserializing it in a safe way.  No other modules should
    read or write the bug files directly.
    
    When working with an issue, it is important to remember that almost all data
    is optional, and defaults to None or the empty list.  In general, data without
    values should be hidden from the user as if it didn't exist at all.
    '''

    def __init__(self,
                 id=None,
                 parent=None, children=[], duplicates=None,
                 creator=None, assigned_to=None, listeners=[],
                 type=None, target=None, severity=None, status=None, resolution=None, category=None,
                 creation_date=None, resolved_date=None, projection=None, estimate=None,
                 title=None, paths=[], description=None, reproduction=None, expected=None, trace=None,
                 comments=[]):
        '''
        The issue constructor takes any of the data that an issue consists of.  (Almost)
        all of the fields are optional.
        
        If an ID is not specified, the issue is considered a new issue, and an ID is generated
        from the title, creation date, and creator, if one exists.  If a creation date is not
        specified, the current system time is used.
        
        If an ID is specified, the issue is considered a preexisting issue, and all other data
        points are left alone.
        
        These two cases guarantee the id attribute will always have a value.  It would be unwise
        to modify this value.
        '''
        self.id = id
        # Relations
        self.parent = parent
        self.children = children
        self.duplicates = duplicates
        # Users
        self.creator = creator
        self.assigned_to = assigned_to
        self.listeners = listeners
        # Status
        self.type = type
        self.target = target
        self.severity = severity
        self.status = status
        self.resolution = resolution
        self.category = category
        # Times
        self.creation_date = creation_date
        self.resolved_date = resolved_date
        self.projection = projection
        self.estimate = estimate
        # Data
        self.title = title
        self.paths = paths
        self.description = description
        self.reproduction = reproduction
        self.expected = expected
        self.trace = trace
        self.comments = comments
        
        if self.id == None:
            if self.creation_date == None:
                self.creation_date = time.time();
                self.id = util.hash(repr(self.creation_date)+self.title+(self.creator if self.creator != None else ''))
    
    def filename(self):
        ''' Returns the suggested filename for this issue '''
        return self.id+".issue"
    
    def to_JSON(self, path, file=None):
        ''' Converts the issue to a JSON datastructure and writes it
        to the specified path and file.
        '''
        if file == None:
            file = self.filename()
        dict = {}
        for k, v in self.__dict__.items():
            if(v != None and v != []):
                dict[k] = v
        json.dump(dict,open(os.path.join(path,file),'w'),
                  indent=1,sort_keys=True)
    
def JSON_to_Issue(file):
    ''' Constructs a new issue from JSON data in the
    specified file '''
    return Issue(**json.load(open(file)))

# unit test on bug reading and writing
if __name__ == '__main__':
    issue = Issue(title="This is a test")
    issue.to_JSON(dir)
    issue2 = JSON_to_Issue(os.path.join(dir,issue.filename()))
    if issue.id == issue2.id:
        print("Looks good")
    else:
        print("Something's wrong, different IDs")
    os.remove(issue.filename())