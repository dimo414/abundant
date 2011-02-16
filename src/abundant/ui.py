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
    
    def write(self,*msg):
        for a in msg:
            self.out.write(str(a))
    
    def alert(self,*msg):
        for a in msg:
            self.err.write(str(a))
    
    def _read(self):
        return self.inp.readline()
    
    def prompt(self,prompt):
        self.write(prompt)
        return self._read()