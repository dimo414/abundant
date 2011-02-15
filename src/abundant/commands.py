# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
This file handles command line tasks after processing
config settings, cli parameters, and any other work

@author: Michael Diamond
Created on Feb 10, 2011
'''

import os
import issue,error
import db as database

# commands ordered alphabetically

def help(ui):
    print("Oh.  Hello.")

def init(ui, dir='.'):
    """Initialize an Abundant database by creating a
    '.ab' directory in the specified directory, or the
    cwd if not otherwise set."""
    db = database.DB(dir,False)
    if db.exists():
        raise error.Abort("Abundant database already exists.")
    # don't need to make db.db because makedirs handles that
    os.makedirs(db.issues)
    os.mkdir(db.cache)
    conf = open(db.conf,"w")
    # write any initial configuration to config file
    conf.close()

def new(ui, db, title, assign_to=None):
    iss = issue.Issue(title=title, assigned_to=assign_to)
    iss.to_JSON(db.issues)
    print("Created new issue with ID %s" % iss.id)
    if assign_to != None:
        print("  Assigned to %s" % assign_to)

# commands listed in order of display
table = {'init':
            (init,
             [('','dir', None, "directory to place database")],
             "[--dir DIR]"),
         'new':
            (new,
             [('a','assign_to', None, "assign the issue to the specified user")],
             "title [-a USER]"),
         'help':
            (help,[],"TODO")}

#command to run on command lookup failure
fallback_cmd = 'help'

# commands that do not need a db object
no_db = ['init','help']