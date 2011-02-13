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
import sys
import commands,error

def handleError(err):
    print(err, file=sys.stderr)
    
    if isinstance(err,error.Abort):
        sys.exit(2)
    
if __name__ == '__main__':
    try:
        commands.init({})
    except Exception as err:
        handleError(err)