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

import os,sys,tempfile,time
from abundant import error,util

class UI:
    def __init__(self,inp=sys.stdin,out=sys.stdout,err=sys.stderr):
        '''Takes file-like objects for input, output,
        and errors.'''
        self.inp = inp
        self.out = out
        self.err = err
        
        #this should eventually parse a config file properly
        self.short_date = '%d/%m/%y %I:%M%p'
        self.long_date = '%a, %b. %d %y at %I:%M:%S%p'
        self.cur_user = 'Michael Diamond'
    
    #
    #Date / Time
    #
    
    def to_short_time(self,timestamp):
        return time.strftime(self.short_date,time.localtime(timestamp))
    
    def to_long_time(self,timestamp):
        return time.strftime(self.long_date,time.localtime(timestamp))
    
    #
    #IO
    #
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
    
    def confirm_positive(self,prompt):
        res = self.prompt(prompt+" (y/n):")
        return res.strip().lower() != 'n'
    
    def edit(self, text):
        '''Launch the user's default editor in order to take more detailed
        input, notably editing an issue.
        
        From Mercurial's ui.py'''
        (fd, name) = tempfile.mkstemp(prefix="ab-editor-", suffix=".txt",
                                      text=True)
        try:
            f = os.fdopen(fd, "w")
            f.write(text)
            f.close()

            editor = self.geteditor()

            util.system("%s \"%s\"" % (editor, name),
                        onerr=error.Abort, errprefix=_("edit failed"))

            f = open(name)
            t = f.read()
            f.close()
        finally:
            os.unlink(name)

        return t
    
    def flush(self):
        '''Fush StdOut and StdErr
        
        From Mercurial ui.py'''
        try: sys.stdout.flush()
        except: pass
        try: sys.stderr.flush()
        except: pass
        