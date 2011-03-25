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
from abundant import error,issue,util
from abundant import db as database

# commands ordered alphabetically

def adduser(ui,db,*args,**opts):
    name = (' '.join(args)).strip()
    if 'email' in opts:
        name = "%s <%s>" % (name,opts['email'].strip())
    f = open(db.users,'a')
    f.write('%s\n' % name)
    f.close()
    ui.write("Added %s to the list of users" % name)

def child(ui,db,child_pref,parent_pref,*args,**opts):
    child = db.get_issue(child_pref)
    parent = db.get_issue(parent_pref)
        
    child.parent = parent.id
    parent.children.append(child.id)
    
    child.to_JSON(db.issues)
    parent.to_JSON(db.issues)
    
    ui.write("Marked issue %s as a child of issue %s" % (child_pref,parent_pref))
    return 0

def details(ui,db,*args,**opts):
    iss = db.get_issue(args[0].strip())
    ui.write(iss.details(ui,db))

def help(ui,*args,**opts):
    ui.write("Help documentation:")
    if len(args) > 0: ui.write("Args: %s" % args)
    out = []
    for k,v in table.items():
        out.append("%s %s" %(k,v[3]))
    ui.write('\n'.join(out))

def init(ui, dir='.',*args,**opts):
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

def list(ui, db, *args, **opts):
    num = 30 # specify the maximum number of results to display
    # use a generator to avoid loading all issues into memory
    iss_iter = (issue.JSON_to_Issue(os.path.join(db.issues,i)) for i in os.listdir(db.issues))
    
    if opts['assigned_to'] != '*':
        user = db.get_user(opts['assigned_to']) if opts['assigned_to'] else None
    if opts['listener']:
        lstset = set([db.get_user(i) for i in opts['listener']])

    list = (i for i in iss_iter
            if (bool(i.resolution) == bool(opts['resolved'])) and
               (opts['assigned_to'] == '*' or i.assigned_to == user) and
               (not opts['listener'] or not set(i.listeners).isdisjoint(lstset)) and
               (not opts['issue'] or i.issue == opts['issue']) and
               (not opts['target'] or i.target == opts['target']) and
               (not opts['severity'] or i.severity == opts['severity']) and 
               (not opts['category'] or i.category == opts['category']) and
               (not opts['creator'] or i.creator == db.get_user(opts['creator'])) and
               (not opts['grep'] or opts['grep'].lower() in i.title.lower())
            )
    
    # we further make a generator out of the print operation to
    # keep large result sets from straining the system unnecessarily
    def writeNext():
        def genLs(ls,num):
            count = 0
            for i in ls:
                ui.write("%s:\t%s" % (db.iss_prefix_obj().prefix(i.id), i.title))
                count += 1
                if count >= num: yield count
            yield count
        gen = genLs(list,num)
        res = next(gen)
        ui.write("Found %s matching issue%s" % (res if res > 0 else "no","" if res == 1 else "s"))
        return res
    
    res = writeNext()
    if res == 0:
        return 1
    while res == num:
        if ui.confirm("More results found, continue printing?",True):
            res = writeNext()
        else: break
    return 0
    
def new(ui, db, *args, **opts):
    
    iss = issue.Issue(title=(' '.join(args)).strip(),
                      assigned_to=db.get_user(opts['assign_to']) if opts['assign_to'] else None,
                      listeners=[db.get_user(i) for i in opts['listener']] if opts['listener'] else None,
                      issue=opts['issue'],
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
    ui.write(iss.descChanges(issue.base,ui))

def tasks(ui, db, user='me', *args, **opts):
    return list(ui, db, assigned_to=user, **opts)

def update(ui, db, prefix, *args, **opts):
    iss = db.get_issue(prefix)
    origiss = db.get_issue(prefix)
    if len(opts) == 0:
        raise error.Abort("Did not specify any updates to make to issue %s" % 
                          db.iss_prefix_obj().pref_str(iss.id))
        
    if opts['assign_to']:
        iss.assigned_to = db.get_user(opts['assign_to'])
    if opts['listener']:
        iss.listeners.extend([db.get_user(i) for i in opts['listener']])
    if opts['rl']:
        for l in [db.get_user(i) for i in opts['rl']]:
            iss.listeners.remove(l)
    if opts['issue']:
        iss.issue = opts['issue']
    if opts['target']:
        iss.target = opts['target']
    if opts['severity']:
        iss.severity = opts['severity']
    if opts['category']:
        iss.category = opts['category']
    
    iss.to_JSON(db.issues)
    
    ui.write("Updated issue %s" % db.iss_prefix_obj().pref_str(iss.id))
    ui.write(iss.descChanges(origiss,ui))

# commands listed in alphabetical order
# the structure is similar to Mercurial's, but
# not identical in syntax
# see util.parse_cli for sytax instructions
table = {'adduser':
            (adduser,
             [util.parser_option('-e','--email')],
             1,
             "NAME [-e EMAIL]"),
         'child':
            (child,
             [],
             2,
             "CHILD_PREFIX PARENT_PREFIX"),
         'details':
            (details,[],1,'prefix'),
         'help':
            (help,[],0,"[topic]"),
         'init':
            (init,
             [
              util.parser_option('--dir')
              ],
              0,
             "[--dir DIR]"),
         'list':
            (list,
             [
              util.parser_option('-a','--assigned_to',default='*',help="issues assigned to this user"),
              util.parser_option('-r','--resolved',action='store_true',default=False,help="the issue is resolved"),
              util.parser_option('-l','--listener',action='append',help="issues being followed by these users"),
              util.parser_option('-i','--issue',help="the type of issue, such as Bug or Feature Request"),
              util.parser_option('-t','--target',help="a target date or milestone for resolution"),
              util.parser_option('-s','--severity',help="the severity of the issue"),
              util.parser_option('-c','--category',help="the category of the issue"),
              util.parser_option('--creator',help="the user filing the bug"),
              util.parser_option('-g','--grep',help="text to match in the title")
              ],
             0,
             "[-a USER] [-r] [-l LISTENER]... [-i ISSUE] [-t TARGET] [-s SEVERITY] "
             "[-c CATEGORY] [--creator USER] [-g SEARCH]"),
         'new':
            (new,
             [
              util.parser_option('-a','--assign_to',help="assign the issue to the specified user"),
              util.parser_option('-l','--listener',action='append',help="user who should follow this issue"),
              util.parser_option('-i','--issue',help="the type of issue, such as Bug or Feature Request"),
              util.parser_option('-t','--target',help="a target date or milestone for resolution"),
              util.parser_option('-s','--severity',help="the severity of the issue"),
              util.parser_option('-c','--category',help="categorize the issue"),
              util.parser_option('-p','--parent',help="specify a parent issue"),
              util.parser_option('-u','--user',help="the user filing the bug")
              ],
              1,
             "title [-a USER] [-l LISTENER]... [-i ISSUE] [-t TARGET] "
             "[-s SEVERITY] [-c CATEGORY] [-u USER]"),
          'tasks':
             (tasks,
              [
               util.parser_option('-r','--resolved',action='store_true',default=False,help="the issue is resolved"),
               util.parser_option('-l','--listener',action='append',help="issues being followed by these users"),
               util.parser_option('-i','--issue',help="the type of issue, such as Bug or Feature Request"),
               util.parser_option('-t','--target',help="a target date or milestone for resolution"),
               util.parser_option('-s','--severity',help="the severity of the issue"),
               util.parser_option('-c','--category',help="the category of the issue"),
               util.parser_option('--creator',help="the user filing the bug"),
               util.parser_option('-g','--grep',help="text to match in the title")
               ],
              0,
              "[assigned_to] [-r] [-l LISTENER]... [-i ISSUE] [-t TARGET] [-s SEVERITY] "
             "[-c CATEGORY] [--creator USER] [-g SEARCH]"),
          'update':
             (update,
              [
               util.parser_option('-a','--assign_to',help="assign the issue to the specified user"),
               util.parser_option('-l','--listener',action='append',help="user who should follow this issue"),
               util.parser_option('--rl','--removelistener',action='append',help="user who should no longer follow this issue"),
               util.parser_option('-i','--issue',help="the type of issue, such as Bug or Feature Request"),
               util.parser_option('-t','--target',help="a target date or milestone for resolution"),
               util.parser_option('-s','--severity',help="the severity of the issue"),
               util.parser_option('-c','--category',help="categorize the issue")
               ],
              1,
              "prefix [-a USER] [-l LISTENER]... [--rl LISTENER]... [-i ISSUE] "
              "[-t TARGET] [-s SEVERITY] [-c CATEGORY]")
        }

#command to run on command lookup failure
fallback_cmd = 'help'

# commands that do not need a db object
no_db = ['init','help']