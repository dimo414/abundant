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
import util,error

class DB(object):
    '''
    A representation of the current database
    '''

    def __init__(self,path):
        '''
        Tries to find an Abundant database in the current or
        parent directory of path.  If it cannot, raises an Abort
        '''
        self.path = util.find_db(path)
        if self.path == None:
            raise error.Abort(
                "No Abundant database found\nLooked for '.ab' directory in all parent directories of %s" % path)
        self.db = os.path.join(self.path,'.ab')
        self.issues = os.path.join(self.db,'issues')
        self.cache = os.path.join(self.db,'.cache')
        