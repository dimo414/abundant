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

import os,time
from abundant import error,issue,util
from abundant import db as database

# commands ordered alphabetically
# the doc comments for functions in this module should
# be considered world readable, as they are served up
# as the help documentation for each command.

def adduser(ui,db,*args,**opts):
    '''Manually add a user to the list of users
    
    When Abundant is aware of the VCS it's residing in,
    it will attempt to load usernames from the VCS.  This
    command can be used to manually add a user who has not
    committed any changes to the repository yet.
    
    All arguments after the command are joined together and
    added to the users file in the Abundant database.
    
    You can also use the -e,--email flag to include an email
    address with the user's name.
    
    Example (the following are functionally identical):
    ab adduser Firstname Lastname -e flastname@example.com
    ab adduser Firstname Lastname <flastname@example.com>    
    '''
    
    name = (' '.join(args)).strip()
    if 'email' in opts:
        name = "%s <%s>" % (name,opts['email'].strip())
    f = open(db.users,'a')
    f.write('%s\n' % name)
    f.close()
    ui.write("Added %s to the list of users" % name)

def child(ui,db,child_pref,parent_pref,*args,**opts):
    '''Mark an issue as a child of another issue
    
    This simply affects the relationship between the
    issues, and does not, for instance, prevent a user
    from resolving the parent issue if they so desire.
    '''
    child = db.get_issue(child_pref)
    parent = db.get_issue(parent_pref)
        
    child.parent = parent.id
    parent.children.append(child.id)
    
    child.to_JSON(db.issues)
    parent.to_JSON(db.issues)
    
    ui.write("Marked issue %s as a child of issue %s" % (child_pref,parent_pref))
    return 0

def comment(ui,db,pref,*args,**opts):
    '''Add a comment to an issue
    
    Appends a time and potentially user-stamped comment
    to the specified issue.  If -m,--message is passed,
    the specified message is used as the comment text.
    Otherwise, an editor is launched and the user is prompted
    to construct a comment.
    '''
    
    iss = db.get_issue(pref)
    
    if opts['message']:
        message = opts['message'].strip()
    else:
        lines = util.ab_strip(ui.edit("AB: Commenting on Issue %s:  %s\n"
                                      "AB: Lines starting with 'AB:' are ignored.\n\n" %
                                      (db.iss_prefix_obj().prefix(iss.id),iss.title)))
        message = ''.join(lines).strip()
        
    if message == '':
        raise error.Abort("Must provide a comment for the specified issue.")
    
    comment = [ui.cur_user,time.time(),message]
    iss.comments.append(comment)
    
    iss.to_JSON(db.issues)
    
    ui.write("Added Comment to Issue %s:" % db.iss_prefix_obj().prefix(iss.id))
    ui.write(issue.comment_to_str(comment))
    
    return 0

def details(ui,db,pref,*args,**opts):
    '''Display all the details and status of the given issue'''
    iss = db.get_issue(pref)
    ui.write(iss.details(ui,db))
    return 0

def edit(ui,db,pref,*args,**opts):
    '''Edit the content of the issue
    
    Notably the fields Paths, Description, Reproduction Steps,
    Expected Result, and Stack Trace.  An editor is launched
    prompting the user to update this data, unless any of these
    are provided at the command line, in which case the
    provided fields are overwritten without launching an editor.
    '''
    
    iss = db.get_issue(pref)
    origiss = db.get_issue(pref)
    
    if opts['paths'] or opts['description'] or opts['reproduction'] or opts['expected'] or opts['trace']:
        iss.paths = opts['paths'] if opts['paths'] else iss.paths
        iss.description = opts['description'] if opts['description'] else iss.description
        iss.reproduction = opts['reproduction'] if opts['reproduction'] else iss.reproduction
        iss.expected = opts['expected'] if opts['expected'] else iss.expected
        iss.trace = opts['trace'] if opts['trace'] else iss.trace
    else:
        formatting = (("Editing Issue %s:  %s\n\n"
                       "[Paths]\n%s\n\n"
                       "[Description]\n%s\n\n"
                       "[Reproduction Steps]\n%s\n\n"
                       "[Expected Result]\n%s\n\n"
                       "[Stack Trace]\n%s") % 
                       (db.iss_prefix_obj().prefix(iss.id),iss.title,
                        util.list2str(iss.paths,True,''),
                        iss.description if iss.description else '',
                        iss.reproduction if iss.reproduction else '',
                        iss.expected if iss.expected else '',
                        iss.trace if iss.trace else ''))
        
        details = util.bracket_strip(util.ab_strip(ui.edit(formatting)))
        
        danger = False
        count = len(details)
        if count != 6:
            if count < 6:
                details+=['']*(6-count)
            danger = True
            
        _, paths, description, reproduction, expected, trace = details[0:6]
        
        if danger:
            ui.alert("Warning: The details could not be parsed cleanly.\n"
                     "This is usually due to inserting or removing sections.")
            ui.alert(("The issue's details will be set to the following:\n"
                      "Paths:\n%s\n\nDescription:\n%s\n\nReproduction Steps:\n%s\n\n"
                      "Expected Results:\n%s\n\nStack Trace:\n%s")
                      % (paths, description, reproduction, expected, trace))
            safe = ui.confirm("Do you want to continue?",False,err=True)
            if not safe:
                raise error.Abort("Failed to parse the details file.")
        
        iss.paths = paths.splitlines()
        iss.description = description if description else None
        iss.reproduction = reproduction if reproduction else None
        iss.expected = expected if expected else None
        iss.trace = trace if trace else None
        
    iss.to_JSON(db.issues)
    
    ui.write("Updated issue %s" % db.iss_prefix_obj().pref_str(iss.id))
    ui.write(iss.descChanges(origiss,ui))
    
    return 0

def help(ui,prefix=None,*args,**opts):
    '''Get help using Abundant'''
    from abundant import abundant
    error = False
    if prefix:
        try:
            cmd = table[abundant.cmdPfx[prefix]]
            
            ui.write(cmd[3])
            ui.write()
            ui.write(cmd[0].__doc__)
            
            ui.write("Options:")
            
            ui.write(util.option_str(cmd[1]))
            
            return 0
            
        except error.UnknownPrefix as err:
            error = True
            ui.alert("Unknown Command: %s" % err.prefix)
        except error.AmbiguousPrefix as err:
            error = True
            ui.alert("Ambiguous Command: %s" % err.prefix)
            ui.alert("Did you mean: %s" % util.list2str(err.choices))
        
    # we don't use else here so that bad command prefixes cause standard help output
    
    ui.write("Abundant Issue Tracking - Version %d.%d\n\nCommands:" 
             % abundant.version)
    
    max_cmd = max([len(i) for i in table.keys()])+3
    out = []
    for cmd in sorted(table):
        str = table[cmd][0].__doc__.splitlines()[0]
        out.append(' '+cmd.ljust(max_cmd)+str)
        if ui.is_verbose():
            out.append('   '+table[cmd][3])
    
    ui.write('\n'.join(out))
    
    return 1 if error else 0 
        
def init(ui, dir='.',*args,**opts):
    '''Initialize an Abundant database
    
    Creates an '.ab' directory in the specified directory,
    or the cwd if not otherwise set.
    '''
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
    '''Get a list of open issues
    
    Called without arguments, list will display all open issues.
    The -r,--resolved flag will instead display resolved issues.
    
    Use the other parameters, detailed below, to further filter
    the issues you wish to see.
    '''
    
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
    
    count = 0
    
    # for now, if the user wants to slow down output, they must pipe output through less/more
    # we ought to be able to do this for them in certain cases
    for i in list:
        ui.quiet(db.iss_prefix_obj().prefix(i.id),ln=False)
        ui.write(":\t%s" % i.title,ln=False)
        ui.quiet()
        count += 1
    
    ui.write("Found %s matching issue%s" % (count if count > 0 else "no","" if count == 1 else "s"))
    
    return 0 if count > 0 else 1

def open(ui, db, prefix, status='Open', *args, **opts):
    '''Opens a previously resolved issue
    
    This command reopens the issue, and optionally sets its
    status to the passed status.'''
    iss = db.get_issue(prefix)
    if not iss.resolution:
        raise error.Abort("Cannot open issue %s, it is already open."
                          "Use resolve to close an open issue." % 
                          db.iss_prefix_obj().pref_str(iss.id))
    
    iss.status = status
    iss.resolution = None
    
    iss.to_JSON(db.issues)
    
    ui.write("Reopened issue %s, set status to %s" % (db.iss_prefix_obj().pref_str(iss.id),iss.status))
    
def new(ui, db, *args, **opts):
    '''Create a new issue
    
    Creates a new open issue and, if set, marks the current user as the creator.
    Options can be used to set additional information about the issue.  See the
    update command to change/add/remove this information from an existing issue. 
    '''
    
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

def resolve(ui, db, prefix, resolution='Resolved', *args, **opts):
    '''Marks an issue resolved
    
    If the issue is not simply "resolved", for instance
    it is concluded it will not be fixed, or it lacks information,
    it may be considered resolved nevertheless.  Therefore you can
    specify a custom resolved status.
    '''
    iss = db.get_issue(prefix)
    if iss.resolution:
        raise error.Abort("Cannot resolve issue %s, it is already resolved with resolution %s."
                          "Use open to reopen a resolved issue." % 
                          (db.iss_prefix_obj().pref_str(iss.id),iss.resolution))
    
    iss.status = 'Resolved'
    iss.resolution = resolution
    
    iss.to_JSON(db.issues)
    
    ui.write("Resolved issue %s with resolution %s" % (db.iss_prefix_obj().pref_str(iss.id),iss.resolution))

def tasks(ui, db, user='me', *args, **opts):
    '''List issues assigned to current user
    
    An alias for list that defaults to showing issues assigned to the
    current user.  A different user can be passed as an argument, and
    all parameters to list except assigned to work as normal.
    '''
    return list(ui, db, assigned_to=user, **opts)

def update(ui, db, prefix, *args, **opts):
    '''Updates the information associated with an issue'''
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

def version(ui, *args, **opts):
    '''Abundant version information and licensing'''
    from abundant import abundant
    ui.write("Abundant Issue Tracking - Version %d.%d" % abundant.version)
    ui.write("Copyright (C) 2011 Michael Diamond\n")
    ui.write("This is free software, released under the GPL 3+ license,\n"
             "available at http://www.gnu.org/licenses/.\n")
    ui.write("This program is distributed in the hope that it will be useful,\n"
             "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
             "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")

# commands listed in alphabetical order
# the structure is similar to Mercurial's, but
# not identical in syntax
# 
# the tuple consists of the following:
#     The function to run
#     a list of optparse Options
#     the number of mandatory positional arguments
#     a usage string
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
         'comment':
            (comment,
             [util.parser_option('-m','--message')],
             1,
             "PREFIX [-m MESSAGE]"),
         'details':
            (details,[],1,"PREFIX"),
         'edit':
            (edit,
             [
              util.parser_option('-p','--paths'),
              util.parser_option('-d','--description'),
              util.parser_option('-r','--reproduction'),
              util.parser_option('-e','--expected'),
              util.parser_option('-t','--trace')
             ],
             0,
             "[-p PATHS] [-d DESCRIPTION] [-r REPRODUCTION] [-e EXPECTED] [-t TRACE]"),
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
              util.parser_option('-C','--creator',help="the user filing the bug"),
              util.parser_option('-g','--grep',help="text to match in the title")
              ],
             0,
             "[-a USER] [-r] [-l LISTENER]... [-i ISSUE] [-t TARGET] [-s SEVERITY] "
             "[-c CATEGORY] [-C USER] [-g SEARCH]"),
         'open':
            (open,[],0,"PREFIX [STATUS]"),
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
          'resolve':
             (resolve,[],0,"PREFIX [RESOLUTION]"),
          'tasks':
             (tasks,
              [
               util.parser_option('-r','--resolved',action='store_true',default=False,help="the issue is resolved"),
               util.parser_option('-l','--listener',action='append',help="issues being followed by these users"),
               util.parser_option('-i','--issue',help="the type of issue, such as Bug or Feature Request"),
               util.parser_option('-t','--target',help="a target date or milestone for resolution"),
               util.parser_option('-s','--severity',help="the severity of the issue"),
               util.parser_option('-c','--category',help="the category of the issue"),
               util.parser_option('-C','--creator',help="the user filing the bug"),
               util.parser_option('-g','--grep',help="text to match in the title")
               ],
              0,
              "[assigned_to] [-r] [-l LISTENER]... [-i ISSUE] [-t TARGET] [-s SEVERITY] "
             "[-c CATEGORY] [-C USER] [-g SEARCH]"),
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
              "[-t TARGET] [-s SEVERITY] [-c CATEGORY]"),
          'version':(version,[],0,"")
        }

#command to run on command lookup failure
fallback_cmd = 'help'

# commands that do not need a db object
no_db = ['init','help','version']