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
import commands,error,prefix,util
import ui as usrint
import db as database

cmdPfx = prefix.Prefix(commands.table.keys())

def exec(cmds,cwd):
    try:
        ui = usrint.UI()
    except:
        sys.stderr.write("FAILED TO CREATE UI OBJECT.\n"
              "This should not have been possible.")
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
            ui.alert("Did you mean: %s" % str(err.choices)[1:-1])
            task = commands.fallback_cmd
            args = []
        
        func, options, args = _parse(task,args)
        
        if task not in commands.no_db:
            db = database.DB(cwd)
            if not db.exists():
                raise error.Abort("No Abundant database found.")
            ret = func(ui,db,*args,**options)
        else:
            ret = func(ui,*args,**options)
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
        ui.alert("Unexpected exception was raised.  This should not happen.")
        ui.alert("Please report the entire output to Michael")
        ui.alert("\nCommand line arguments:\n  ",' '.join(sys.argv))
        traceback.print_exception(exc_type,exc_value,exc_traceback)
        return 10

def _parse(task,args):
    entry = commands.table[task]
    if entry == None:
        raise error.SeriousAbort("_parse should only be passed actual "
                                 "commands that are known to exist.")
    
    try:
        options,arg = util.parse_cli(args,entry[1])
    except Exception as err:
        err.task = task # we know what task, so record that
        raise
    
    if len(arg) < entry[2]:
        raise error.MissingArguments(task)
    
    return (entry[0], options.__dict__, arg)
        
if __name__ == '__main__':
    sys.stdout.write("Welcome to Abundant:\n")
    while True:
        line = sys.stdin.readline()
        if line.strip().lower() == 'exit': break
        args = line.strip().split(' ')
        ret = exec(args,os.getcwd())
        sys.stderr.flush()
        sys.stdout.flush()
        sys.stderr.write("Return Code: %d\n" % ret)
        sys.stderr.flush()