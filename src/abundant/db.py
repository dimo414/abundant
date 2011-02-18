# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
This class represents the current database the command is
working against.

@author: Michael Diamond
Created on Feb 13, 2011
'''

import os
import error,issue,prefix,util

class DB(object):
    '''
    A representation of the current database
    '''

    def __init__(self,path,recurse=True):
        '''
        Tries to find an Abundant database in the current or
        parent directory of path.  If it cannot, constructs what
        database should look like, use exists() to check for existence
        '''
        self.search = path
        self.path = None
        if recurse:
            self.path = util.find_db(path)
        if self.path == None:
            self.path = path
        self.path = os.path.abspath(self.path)
        self.db = os.path.join(self.path,'.ab')
        self.issues = os.path.join(self.db,'issues')
        self.cache = os.path.join(self.db,'.cache')
        self.conf = os.path.join(self.db,"ab.conf")
        
    def exists(self):
        return os.path.exists(self.db)
    
    def prefix_obj(self):
        try:
            return self._prefix
        except AttributeError:
            list = [i.replace(issue.ext,'') for i in os.listdir(self.issues)]
            self._prefix = prefix.Prefix(list)
        return self._prefix
    
    def get_issue_prefix(self,id):
        return self.prefix_obj().prefix(id)
    
    def get_issue(self,pref):
        return issue.JSON_to_Issue(os.path.join(self.issues,self.get_issue_id(pref)+issue.ext))
    
    def get_issue_id(self,pref):
        try:
            return self.prefix_obj()[pref]
        except error.AmbiguousPrefix as err:
            def choices(issLs):
                ls = [self.get_issue(i) for i in 
                        (issLs[:2] if len(issLs) > 3 else issLs[:])]
                return ', '.join([self.get_issue_prefix(i.id)+(':'+i.title if i.title else '') for i in ls])
                
            raise error.Abort("Issue prefix %s is ambiguous\n  Suggestions: %s" % (err.prefix,choices(err.choices)))
        except error.UnknownPrefix as err:
            raise error.Abort("Issue prefix %s does not correspond to any issues" % err.prefix)
    
    def get_issue_id_str(self,id):
        pref = self.get_issue_prefix(id)
        return pref+':'+id[len(pref):]
