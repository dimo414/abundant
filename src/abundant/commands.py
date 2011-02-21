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

def child(ui,db,child_pref,parent_pref):
    child = db.get_issue(child_pref)
    parent = db.get_issue(parent_pref)
        
    child.parent = parent.id
    parent.children.append(child.id)
    
    child.to_JSON(db.issues)
    parent.to_JSON(db.issues)
    
    ui.write("Marked issue %s as a child of issue %s" % (child_pref,parent_pref))
    return 0

def help(ui,*args):
    ui.write("Help documentation goes here.")
    ui.write(args)
    return 0

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
    conf = open(db.conf,'w')
    # write any initial configuration to config file
    conf.close()
    usr = open(db.users,'w')
    usr.close()
    
    ui.write("Created Abundant issue database in %s" % db.path)
    return 0

def new(ui, db, *args, **opts):
    iss = issue.Issue(title=(' '.join(args)).strip(),
                      assigned_to=db.get_user(opts['assign_to']) if opts['assign_to'] else None,
                      listeners=[db.get_user(i) for i in opts['listener']] if opts['listener'] else None,
                      type=opts['type'],
                      severity=opts['severity'],
                      category=opts['category'],
                      parent=db.get_issue_id(opts['parent']) if opts['parent'] else None,
                      creator=db.get_user(opts['user']) if opts['user'] else None
                      )
    if opts['parent']:
        parent = db.get_issue(opts['parent'])
        parent.children.append(iss.id)
        parent.to_JSON(db.issues)
    
    db.iss_prefix_obj().add(iss.id)
    iss.to_JSON(db.issues)
    
    ui.write("Created new issue with ID %s" % db.iss_prefix_obj().pref_str(iss.id))
    ui.write(iss.descChanges(issue.base))
    return 0

def tasks(ui, db, user=None):
    list = [issue.JSON_to_Issue(os.path.join(db.issues,i)) for i in os.listdir(db.issues)]
    list = [i for i in list if user is None or i.assigned_to == user]
    ln = len(list)
    
    ui.write("Found %s issue%s assigned to %s" % 
             (ln if ln > 0 else "no","" if ln == 1 else "s", user if user is not None else "anybody"))
    if len(list) > 0:
        for i in list:
            ui.write("%s:\t%s" % (db.iss_prefix_obj().prefix(i.id), i.title))
        return 0
    else:
        return 1

# commands listed in alphabetical order
# the structure is similar to Mercurial's, but
# not identical in syntax
# see util.parse_cli for sytax instructions
table = {'child':
            (child,
             [],
             2,
             "SOMETHING"),
         'help':
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
              util.parser_option('-p','--parent',help="specify a parent issue"),
              util.parser_option('-u','--user',help="the user filing the bug")
              ],
              1,
             "title [-a USER] [-l LISTENER]... [-t TYPE] [--target TARGET] "
             "[-s SEVERITY] [-c CATEGORY] [-u USER]"),
          'tasks':
             (tasks,
              [],
              0,
              "tasks [assigned_to]")
        }

#command to run on command lookup failure
fallback_cmd = 'help'

# commands that do not need a db object
no_db = ['init','help']