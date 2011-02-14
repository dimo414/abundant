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
import commands,error,fancyopts,prefix
import db as database

cmdPfx = prefix.Prefix(commands.table.keys())

def exec(cmds,cwd):
    try:
        if len(cmds) < 1:
            prefix = 'commands'
            args = []
        else:
            prefix = cmds[1]
            args = cmds[2:]
        
        # load config settings
        
        try:
            task = cmdPfx[prefix]
        except error.UnknownPrefix as err:
            print("Unknown Command: %s\n" % err.prefix)
            task = 'commands'
        except error.AmbiguousPrefix as err:
            print("Ambiguous Command: %s" % err.prefix)
            print("Did you mean: %s\n" % str(err.choices)[1:-1])
            task = 'commands'
        
        ui = {}
        
        func, args, options = _parse(task,args)
        
        if task not in commands.no_db:
            db = database.DB(cwd)
            func(ui,db,*args,**options)
        else:
            func(ui,*args,**options)
            
        # Global error handling starts here
    except error.Abort as err:
        print("Abort:",err,file=sys.stderr)
        sys.exit(2)
    except error.CommandError as err:
        print("Invalid Command:",err,file=sys.stderr)
        sys.exit(3)
        
    except Exception as err:
        '''Exceptions we were not expecting.'''
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Unexpected exception was raised.  This should not happen.",file=sys.stderr)
        print("Please report the entire output to Michael",file=sys.stderr)
        print("\nCommand line arguments:\n",sys.argv,file=sys.stderr)
        print(file=sys.stderr)
        traceback.print_exception(exc_type,exc_value,exc_traceback)
        sys.exit(10)

def _parse(task,args):
    options = {}
    entry = commands.table[task]
    try:
        args = fancyopts.fancyopts(args, entry[1], options)
    except fancyopts.getopt.GetoptError as err:
        raise error.CommandError(err)
    
    return (entry[0], args, options)
        
if __name__ == '__main__':
    args = "new BADABOOOOP".split()
    sys.argv.extend(args)
    exec(sys.argv,os.getcwd())