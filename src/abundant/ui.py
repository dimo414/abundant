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

quiet = 0
normal = 1
verbose = 2
debug = 3

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
        self.cur_user = 'Test User'
        
        self.volume = normal
    
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
    def set_volume(self,volume):
        '''Set the ui object's volume'''
        self.volume = volume
    
    def write(self,*msg,ln=True,volume=normal):
        '''Write a message to the output stream.

        The ui object's volume must be as high as the message volume to actually output.'''
        if self.volume >= volume:
            for a in msg:
                self.out.write(str(a))
            if ln: self.out.write('\n')
            
    def quiet(self,*msg,ln=True):
        '''Write a message to the output stream, even if quiet.'''
        self.write(*msg,ln=ln,volume=quiet)
    
    def verbose(self,*msg,ln=True):
        '''Write a verbose message to the output stream.
        
        Only happens if ui's volume is set to verbose or higher'''
        self.write(*msg,ln=ln,volume=verbose)
    
    def debug(self,*msg,ln=True):
        '''Write a debug message to the output stream.
        
        Only happens if ui's volume is set to debug or higher'''
        self.write(*msg,ln=ln,volume=debug)
    
    def alert(self,*msg,ln=True):
        '''Writes a message to the error stream.  Not affected by volume.'''
        for a in msg:
            self.err.write(str(a))
        if ln: self.err.write('\n')
    
    def _read(self):
        '''Read a line of input'''
        self.flush()
        return self.inp.readline()
    
    def prompt(self,prompt,volume=normal):
        '''Prompt the user, then return input, or nothing if volume is too low'''
        if self.volume < volume: # if nothing would be output
            return ''
        self.write(prompt,ln=False,volume=volume)
        return self._read()
    
    def confirm(self,prompt,default,volume=normal):
        '''Asks the user to confirm an action.
        
        Default is returned if volume is too low.  Additionally,
        default determines how unusual input is handled.  If default
        is false, the user must expressly say y or yes to confirm;
        if default is true, the user must expressly say n or no to deny.'''
        res = self.prompt(prompt+" (y/n): ",volume=volume).strip()
        if res == '':
            return default
        res = res.lower()[0]
        return (default and res != 'n') or (not default and res == 'y')
    
    def edit(self, text):
        '''Launch the user's default editor in order to take more detailed
        input, notably editing an issue.
        
        From Mercurial's ui.py'''
        (fd, name) = tempfile.mkstemp(prefix="ab-editor-", suffix=".txt",
                                      text=False)
        try:
            f = os.fdopen(fd, "w")
            f.write(text)
            f.close()

            editor = self.geteditor()

            util.system("%s \"%s\"" % (editor, name),
                        onerr=error.Abort, errprefix="Edit failed")

            f = open(name)
            t = f.read()
            f.close()
        finally:
            os.unlink(name)

        return t
    
    def geteditor(self):
        return 'notepad'
    
    def flush(self):
        '''Fush StdOut and StdErr
        
        From Mercurial ui.py'''
        try: sys.stdout.flush()
        except: pass
        try: sys.stderr.flush()
        except: pass
        