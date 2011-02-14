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
import sys,traceback
import commands,error
    
if __name__ == '__main__':
    try:
        commands.init({})
        
        # Global error handling starts here
    except error.Abort as err:
        print("Abort:",err,file=sys.stderr)
        
    except Exception as err:
        '''Exceptions we were not expecting.'''
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Unexpected exception was raised.  This should not happen.",file=sys.stderr)
        print("Please report the entire output to Michael",file=sys.stderr)
        print("\nCommand line arguments:\n",sys.argv,file=sys.stderr)
        print(file=sys.stderr)
        traceback.print_exception(exc_type,exc_value,exc_traceback)
        