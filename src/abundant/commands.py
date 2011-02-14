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

def init(ui, path='.'):
    """Initialize an Abundant database by creating a
    '.ab' directory in the specified directory, or the
    cwd if not otherwise set."""
    db = database.DB(path,False)
    if db.exists():
        raise error.Abort("Abundant database already exists.")
    # don't need to make db.db because makedirs handles that
    os.makedirs(db.issues)
    os.mkdir(db.cache)
    conf = open(db.conf,"w")
    # write any initial configuration to config file
    conf.close()

def new(ui, db, title, assigned_to=None):
    iss = issue.Issue(title=title, assigned_to=assigned_to)
    iss.to_JSON(db.issues)
    print("Created new issue with ID %s" % iss.id)
    if assigned_to != None:
        print("  Assigned to %s" % assigned_to)