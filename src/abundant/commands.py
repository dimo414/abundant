# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
This file handles the actual functionality of
command line tasks.  There is a one-to-one mapping
of command line tasks to functions in this module.

@author: Michael Diamond
Created on Feb 10, 2011
'''

import os
import error,issue,util
import db as database

# commands ordered alphabetically

def child(ui,db,child,parent):
    child = db.get_issue(child)
    parent = db.get_issue(parent)
        
    

def help(ui,*args):
    ui.write("Help documentation goes here.")
    ui.write(args)

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

def new(ui, db, *args, **opts):
    iss = issue.Issue(title=(' '.join(args)).strip(),
                      assigned_to=opts['assign_to'],
                      listeners=opts['listener'],
                      type=opts['type'],
                      severity=opts['severity'],
                      category=opts['category'],
                      creator=opts['user']
                      )
    iss.to_JSON(db.issues)
    ui.write("Created new issue with ID %s" % iss.id)
    ui.write(iss.descChanges(issue.base))

# commands listed in order of display
# the structure is similar to Mercurial's, but
# not identical in syntax
# see util.parse_cli for sytax instructions
table = {'help':
            (help,[],0,"[topic]"),
         'init':
            (init,
             [
              util.parser_option('--dir')
              ],
              0,
             "[--dir DIR]"),
         'new':
            (new,
             [
              util.parser_option('-a','--assign_to',help="assign the issue to the specified user"),
              util.parser_option('-l','--listener',action='append',help="user who should follow this issue"),
              util.parser_option('-t','--type',help="the type of issue, such as Bug or Feature Request"),
              util.parser_option('--target',help="a target date or milestone for resolution"),
              util.parser_option('-s','--severity',help="the severity of the issue"),
              util.parser_option('-c','--category',help="categorize the issue"),
              util.parser_option('-u','--user',help="the user filing the bug")
              ],
              1,
             "title [-a USER] [-l LISTENER]... [-t TYPE] [--target TARGET] "
             "[-s SEVERITY] [-c CATEGORY] [-u USER]"),
         'child':
            (child,
             [],
             2,
             "SOMETHING")
        }

#command to run on command lookup failure
fallback_cmd = 'help'

# commands that do not need a db object
no_db = ['init','help']