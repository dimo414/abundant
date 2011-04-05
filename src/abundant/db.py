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
from abundant import error,issue,prefix,util

class DB(object):
    '''
    A representation of the current database
    '''

    def __init__(self,path,recurse=True,ui=None):
        '''
        Tries to find an Abundant database in the current or
        parent directory of path.  If it cannot, constructs what
        database should look like, use exists() to check for existence
        '''
        path = os.path.abspath(path)
        self.search = path
        self.path = None
        self.ui = ui
        if recurse:
            self.path = util.find_db(path)
        if self.path == None:
            self.path = path
        self.db = os.path.join(self.path,'.ab')
        self.issues = os.path.join(self.db,'issues')
        self.cache = os.path.join(self.db,'.cache')
        self.conf = os.path.join(self.db,"ab.conf")
        self.local_conf = os.path.join(self.db,"ab.local.conf")
        self.users = os.path.join(self.db,"users")
        
        self._usr_prefix = None
        self._iss_prefix = None
        
    def exists(self):
        return os.path.exists(self.db)
    
    def usr_prefix_obj(self):
        if self._usr_prefix is None:
            self._usr_prefix = prefix.Prefix()
            try:
                for line in open(self.users, 'r'):
                    line = line.strip()
                    if line == '' or line[0] == '#':
                        continue
                    self._usr_prefix.add(line)
                    lt = line.find('<')
                    gt = line.find('>')
                    if lt >= 0 and gt >= 0 and gt > lt:
                        self._usr_prefix.alias(line[lt+1:gt], line)
            except IOError:
                pass # file doesn't exist, nbd
            except: raise
            if self.ui.config('ui','username'):
                try:
                    self._usr_prefix.alias('me',self.ui.config('ui','username'))
                except error.UnknownPrefix:
                    raise error.Abort("The specified current user, '%s', does not exist.  "
                                      "Use `adduser` to add it" % self.ui.config('ui','username'))
        return self._usr_prefix
    
    def get_user(self,prefix):
        try:
            if 'nobody'.startswith(prefix.lower()): return None
            return self.usr_prefix_obj()[prefix]
        except error.AmbiguousPrefix as err:
            raise error.Abort("User prefix %s is ambiguous\n  Suggestions: %s" % (err.prefix,err.choices))
        except error.UnknownPrefix as err:
            raise error.Abort("User prefix %s does not correspond to any known user" % err.prefix)
    
    def iss_prefix_obj(self):
        if self._iss_prefix is None:
            list = [i.replace(issue.ext,'') for i in os.listdir(self.issues)]
            self._iss_prefix = prefix.Prefix(list)
        return self._iss_prefix
    
    def get_issue(self,pref):
        return issue.JSON_to_Issue(os.path.join(self.issues,self.get_issue_id(pref)+issue.ext))
    
    def get_issue_id(self,pref):
        try:
            return self.iss_prefix_obj()[pref]
        except error.AmbiguousPrefix as err:
            def choices(issLs):
                ls = [self.get_issue(i) for i in 
                        (issLs[:2] if len(issLs) > 3 else issLs[:])]
                return ', '.join([self.iss_prefix_obj().prefix(i.id)+(':'+i.title if i.title else '') for i in ls])
                
            raise error.Abort("Issue prefix %s is ambiguous\n  Suggestions: %s" % (err.prefix,choices(err.choices)))
        except error.UnknownPrefix as err:
            raise error.Abort("Issue prefix %s does not correspond to any issues" % err.prefix)
    