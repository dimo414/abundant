# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
This file handles command line tasks after processing
config settings, cli parameters, and any other work

@author: Michael Diamond
Created on Feb 10, 2011
'''

import os
import util

def init(ui, path='.'):
    """Initialize an Abundant database by creating a
    '.ab' directory in the specified directory, or the
    cwd if not otherwise set."""
    path = os.path.abspath(path)
    print(path)
    util.makedirs(path+os.sep+".ab")
    