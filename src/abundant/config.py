# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.
#
# This file is a fork of config.py  from Mercurial, used with permission
# under the GPL.  The copyright header from Mercurial's version of the
# file is included below:

# config.py - configuration parsing for Mercurial
#
#  Copyright 2009 Matt Mackall <mpm@selenic.com> and others
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

'''
Taken from Mercurial, this file parses config files
to use to customize Abundant's behavior per computer
and per repository 

@author: Michael Diamond
Created on Feb 10, 2011
'''

from abundant import error,util
import re, os

class sortdict(dict):
    '''a simple sorted dictionary'''
    def __init__(self, data=None):
        self._list = []
        if data:
            self.update(data)
    def copy(self):
        return sortdict(self)
    def __setitem__(self, key, val):
        if key in self:
            self._list.remove(key)
        self._list.append(key)
        dict.__setitem__(self, key, val)
    def __iter__(self):
        return self._list.__iter__()
    def update(self, src):
        for k in src:
            self[k] = src[k]
    def items(self):
        return [(k, self[k]) for k in self._list]
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._list.remove(key)

class config(object):
    '''Constructs a config object, a 2D dict of sections to keys to values'''
    def __init__(self, data=None):
        self._data = {}
        self._source = {}
        if data:
            for k in data._data:
                self._data[k] = data[k].copy()
            self._source = data._source.copy()
    def copy(self):
        return config(self)
    def __contains__(self, section):
        return section in self._data
    def __getitem__(self, section):
        return self._data.get(section, {})
    def __iter__(self):
        for d in self.sections():
            yield d
    def update(self, src):
        for s in src:
            if s not in self:
                self._data[s] = sortdict()
            self._data[s].update(src._data[s])
        self._source.update(src._source)
    def get(self, section, item, default=None):
        return self._data.get(section, {}).get(item, default)
    def source(self, section, item):
        return self._source.get((section, item), "")
    def sections(self):
        return sorted(self._data.keys())
    def items(self, section):
        return self._data.get(section, {}).items()
    def set(self, section, item, value, source=""):
        if section not in self:
            self._data[section] = sortdict()
        self._data[section][item] = value
        self._source[(section, item)] = source

    def parse(self, src, data, sections=None, remap=None, include=None):
        '''Parses a string as a config file
        
        src: the path or origin of the data being parse
        data: the data to parse, a string
        sections: if set, will only parse the given sections
        remap: if set, will remap the given sections to different names
        include: if set, will be used to include sub-config files
        '''
        
        sectionre = re.compile(r'\[([^\[]+)\]')
        itemre = re.compile(r'([^=\s][^=]*?)\s*=\s*(.*\S|)')
        contre = re.compile(r'\s+(\S|\S.*\S)\s*$')
        emptyre = re.compile(r'(;|#|\s*$)')
        unsetre = re.compile(r'%unset\s+(\S+)')
        includere = re.compile(r'%include\s+(\S|\S.*\S)\s*$')
        section = ""
        item = None
        line = 0
        cont = False

        for l in data.splitlines(True):
            line += 1
            if cont:
                m = contre.match(l)
                if m:
                    if sections and section not in sections:
                        continue
                    v = self.get(section, item) + "\n" + m.group(1)
                    self.set(section, item, v, "%s:%d" % (src, line))
                    continue
                item = None
                cont = False
            m = includere.match(l)
            if m:
                inc = util.expandpath(m.group(1))
                base = os.path.dirname(src)
                inc = os.path.normpath(os.path.join(base, inc))
                if include:
                    try:
                        include(inc, remap=remap, sections=sections)
                    except IOError as inst:
                        raise error.ConfigError("cannot include %s (%s)"
                                               % (inc, inst.strerror),
                                               "%s:%s" % (src, line))
                continue
            if emptyre.match(l):
                continue
            m = sectionre.match(l)
            if m:
                section = m.group(1)
                if remap:
                    section = remap.get(section, section)
                if section not in self:
                    self._data[section] = sortdict()
                continue
            m = itemre.match(l)
            if m:
                item = m.group(1)
                cont = True
                if sections and section not in sections:
                    continue
                self.set(section, item, m.group(2), "%s:%d" % (src, line))
                continue
            m = unsetre.match(l)
            if m:
                name = m.group(1)
                if sections and section not in sections:
                    continue
                if self.get(section, name) is not None:
                    del self._data[section][name]
                continue

            raise error.ConfigError(l.rstrip(), ("%s:%s" % (src, line)))

    def read(self, path, fp=None, sections=None, remap=None):
        '''Reads a config file given a filename and a handle to the file
        
        See parse for other argument info'''
        self.parse(path, fp.read(), sections, remap, self.read)
