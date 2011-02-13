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

class Abort(Exception):
    """Raised if a command cannot continue."""