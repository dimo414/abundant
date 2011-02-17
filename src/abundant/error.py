# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
Contains all our system exceptions in one place

@author: Michael Diamond
Created on Feb 12, 2011
'''

# Global exceptions

class Abort(Exception):
    '''Raised if a command cannot continue.'''

class NoSuchIssue(Abort):
    '''Raised if a requested issue does not exist.'''

class SeriousAbort(Abort):
    '''Raised when the issue should have been previously prevented
    in the code.''' 

class CommandError(Exception):
    '''Raised if input to the command is invalid, wrong, or missing required fields'''

class ParsingError(CommandError):
    '''Raised to indicate parsing the command line failed'''

class MissingArguments(CommandError):
    '''Raised if the command expected more arguments than it received'''
    def __init__(self,task,*args):
        Exception.__init__(self,"%s expected more arguments." % task,*args)
        self.task = task

# Prefix Exceptions

class UnknownPrefix(Exception):
    '''Raised if a given prefix does not map to any items'''
    def __init__(self,prefix,*args):
        Exception.__init__(self,*args)
        self.prefix = prefix

class AmbiguousPrefix(Exception):
    '''Raised if a given prefix maps to multiple items'''
    def __init__(self,prefix,choices,*args):
        Exception.__init__(self,*args)
        self.prefix = prefix
        self.choices = choices