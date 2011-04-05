# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
A simple interactive interface to Abundant for testing

@author: Michael Diamond
Created on Mar 14, 2011
'''

import os,sys
from abundant import abundant

sys.stdout.write("Welcome to Abundant:\n")
while True:
    line = sys.stdin.readline()
    if line.strip().lower() == 'exit': break
    args = line.strip().split(' ')
    ret = abundant.exec(args,os.getcwd())
    sys.stderr.flush()
    sys.stdout.flush()
    sys.stderr.write("Return Code: %d\n" % ret)
    sys.stderr.flush()