# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
A data structure which handles IO and configuration

Many methods modeled from Mercurial

@author: Michael Dimaond
Created on Feb 16, 2011
'''

import sys

class UI:
    def __init__(self,inp=sys.stdin,out=sys.stdout,err=sys.stderr):
        '''Takes file-like objects for input, output,
        and errors.'''
        self.inp = inp
        self.out = out
        self.err = err
    
    def write(self,*msg,ln=True):
        for a in msg:
            self.out.write(str(a))
        if ln: self.out.write('\n')
    
    def alert(self,*msg,ln=True):
        for a in msg:
            self.err.write(str(a))
        if ln: self.err.write('\n')
    
    def _read(self):
        '''Read a line of input'''
        return self.inp.readline()
    
    def prompt(self,prompt):
        '''Prompt the user, then return input'''
        self.write(prompt)
        return self._read()
    
    def flush(self):
        '''Fush StdOut and StdErr
        
        From Mercurial ui.py'''
        try: sys.stdout.flush()
        except: pass
        try: sys.stderr.flush()
        except: pass
        