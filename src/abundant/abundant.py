# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
Main module, handles parsing the CLI arguments, loading config
data, and passing work off to commands

@author: Michael Diamond
Created on Feb 10, 2011
'''
import os,sys,traceback
from abundant import commands,error,prefix,util
from abundant import ui as usrint
from abundant import db as database

#Major/Minor release number.
#Any updates to this should be tagged change sets.
version = (0,3)

cmdPfx = prefix.Prefix(commands.table.keys())

globalArgs = [util.parser_option('-D','--database',help="the directory to search for the Abundant database"),
              util.parser_option('-q','--quiet',action='store_const',const=usrint.quiet,dest='volume',default=usrint.normal,
                                 help="Limit output to errors and unexpected data"),
              util.parser_option('-v','--verbose',action='store_const',const=usrint.verbose,dest='volume',
                                 help="Output additional content the user wouldn't usually need"),
              util.parser_option('--debug',action='store_const',const=usrint.debug,dest='volume',
                                 help="Output debug information useful for development / debugging"),
              util.parser_option('-h','--help',action="store_true")]

def exec(cmds,cwd):
    try:
        ui = usrint.UI()
    except:
        sys.stderr.write("FAILED TO CREATE UI OBJECT.\n"
              "This should not have been possible.\n"
              "Please report this issue immediately.\n\n")
        raise
    try:
        
        if len(cmds) < 1:
            prefix = commands.fallback_cmd
            args = []
        else:
            prefix = cmds[0]
            args = cmds[1:]
        
        # load config settings
        
        try:
            task = cmdPfx[prefix]
            
        except error.UnknownPrefix as err:
            ui.alert("Unknown Command: %s" % err.prefix)
            task = commands.fallback_cmd
            args = []
        except error.AmbiguousPrefix as err:
            ui.alert("Ambiguous Command: %s" % err.prefix)
            ui.alert("Did you mean: %s" % util.list2str(err.choices))
            task = commands.fallback_cmd
            args = []
        
        func, options, args_left = _parse(task,args)
        
        #set volume
        ui.set_volume(options['volume'])
        
        #check for -h,--help
        if options['help']:
            new_args = [task] + args
            task = commands.fallback_cmd
            func, options, args_left = _parse(task,new_args)
        
        if task not in commands.no_db:
            path = os.path.join(cwd,options['database']) if options['database'] else cwd
            
            db = database.DB(path,ui=ui)
            if not db.exists():
                raise error.Abort("No Abundant database found.")
            ui.db_conf(db)
            ret = func(ui,db,*args_left,**options)
        else:
            ret = func(ui,*args_left,**options)
        if ret is None:
            return 0
        else: return ret
            
        # Global error handling starts here
    except error.Abort as err:
        ui.alert("Abort: ",err)
        return 2
    except error.CommandError as err:
        ui.alert("Invalid Command:\n",err)
        try:
            ui.flush() # ensure error displays first
            exec([commands.fallback_cmd,err.task],cwd)
        except:
            # if there is no err.task then don't bother outputting help on it
            pass
        return 3
        
    except Exception as err:
        '''Exceptions we were not expecting.'''
        exc_type, exc_value, exc_traceback = sys.exc_info()
        sys.stderr.write("Unexpected exception was raised.  This should not happen.\n")
        sys.stderr.write("Please report the entire output to Michael\n")
        sys.stderr.write("\nCommand line arguments:\n  %s\n" % ' '.join(sys.argv))
        traceback.print_exception(exc_type,exc_value,exc_traceback)
        return 10

def _parse(task,args):
    entry = commands.table[task]
    if entry == None:
        raise error.SeriousAbort("_parse should only be passed actual "
                                 "commands that are known to exist.")
    
    try:
        options,arg = util.parse_cli(args,globalArgs+entry[1])
    except Exception as err:
        err.task = task # we know what task, so record that
        raise
    
    if len(arg) < entry[2] and not options.help:
        raise error.MissingArguments(task)
    
    return (entry[0], options.__dict__, arg)
