# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
A set of utility operations used throughout Abundant.

@author: Michael Diamond
Created on Feb 7, 2011
'''

import hashlib, optparse, os, re, subprocess, sys, time
from abundant import error

def hash(text):
    '''Return a hash of the given text for use as an id.
    
    Currently SHA1 hashing is used.  It should be plenty for our purposes.'''
    return hashlib.sha1(text.encode('utf-8')).hexdigest()

def find_db(p):
    '''Identifies the issue database to work with
    
    From Mercurial cmdutil.py'''
    while not os.path.isdir(os.path.join(p, ".ab")):
        oldp, p = p, os.path.dirname(p)
        if p == oldp:
            return None

    return p

def list2str(ls,lines=False,pad='  '):
    '''Returns a list as a pretty string'''
    try:
        if isinstance(ls,str):
            raise TypeError("Don't iter on strings")
        ls = (str(i) for i in ls)
        if lines:
            return ('\n'+pad).join(ls)
        return ', '.join(ls)
    except:
        return str(ls)

_split_pat = re.compile(r'\s*,\s*')
def split_list(string):
    '''Splits a string of comma separated items into a list'''
    return _split_pat.split(string.strip())

def expandpath(path):
    '''Expands system variables in paths
    
    such as ~ or %USERPROFILE%
    
    Taken from Mercurial's util.py
    ''' 
    return os.path.expanduser(os.path.expandvars(path))

_configpath = None

def configpaths():
    '''returns all locations to look for config files,
    excluding repo-specific paths.
    
    Currently this is very limited, but should work for our
    purposes at the moment.  At present, the result of this
    function contains paths for multiple os's, and as such
    they cannot be trusted to necessarily even be valid paths. 
    
    Styled after Mercurial's rcpath() in util.py
    '''
    
    global _configpath
    if _configpath is None:
        execpath = os.path.dirname(sys.argv[0])
        #later should override earlier
        path = [os.path.join(i,'ab.conf') for i in 
                   ['/etc/abundant',
                    execpath,
                    os.path.join(os.path.join(os.path.dirname(execpath),'etc'),'abundant'),
                    '%APPDATA%',
                    '%HOMEPATH%',
                    '%USERPROFILE%']
                ]
        path.append(os.path.join('~','.ab.conf'))
        
        if 'ABCONFPATH' in os.environ:
            for p in os.environ['ABCONFPATH'].split(os.pathsep):
                if not p:
                    continue
                path.append(p)
        
        _configpath = [expandpath(p) for p in path]
    
    return _configpath

def diff_dict(to,fro):
    '''Identifies and returns the differences between
    two dicts as a dictionary of fields to tuples 
    where the first entry in the tuple is the to value,
    or None if the data was removed, and the second entry
    is the from value, or None if the data was added.
    
    If an item in the dict is a list, it will identify
    differences between the two lists, and the tuple contains
    data added and data removed from the list.
    
    Note that this method explicitly treats None and []
    as nonexistent for the sake of the diff.'''
    diff = {}
    def empty(dict,key):
        return dict[key] == None or dict[key] == []
    
    for key in fro.keys():
        if key not in to or empty(to,key) and not empty(fro,key):
            diff[key] = (None,fro[key])
    for key in to.keys():
        if key not in fro or empty(fro,key) and not empty(to,key):
            diff[key] = (to[key],None)
        elif to[key] != [] and fro[key] != [] and to[key] != fro[key]:
            if isinstance(to[key],list) and isinstance(fro[key],list):
                to_set = set(to[key])
                fro_set = set(fro[key])
                diff[key] = ([i for i in to_set.difference(fro_set)],
                             [i for i in fro_set.difference(to_set)])
            else:
                diff[key] = (to[key],fro[key])  
    return diff 

parser_option = optparse.make_option

class _ThrowParser(optparse.OptionParser):
    def error(self, msg):
        """Overrides optparse's default error handling
        and instead raises an exception which will be caught upstream
        """
        raise optparse.OptParseError(msg)

def parse_cli(args, opts):
    '''Parses command line input into options and positional arguments
    
    Takes a list of arguments to the command line, and a
    list of options, constructed from parser_option(), and
    returns a tuple of the remaining positional arguments
    and the options parsed out of the arguments.
    '''
    # help is handled elsewhere
    parser = _ThrowParser(add_help_option=False,option_list=opts)
    
    try:
        return parser.parse_args(args)
    except optparse.OptParseError as err:
        raise error.ParsingError(err.msg)
    
def option_str(options):
    '''Constructs an option string
    
    Based on optparse.HelpFormatter code and styled after 
    Mercurial's help output, turns an optparse.Option into
    a string for displaying help info.
    '''
    
    max_len = 80
    multi_set = set(['append','append_const','count'])
    
    optstrs = []
    for option in options:
        str = (' ' + ' '.join(i for i in option._short_opts) + 
               ' ' + ' '.join(i for i in option._long_opts))
        if option.takes_value():
            metavar = option.metavar or option.dest.upper()
            str = "%s %s" % (str,metavar)
        if option.action in multi_set:
            str = "%s %s" % (str,'[+]')
        optstrs.append((str,option.help if option.help else ''))
    
    opt_len = max([len(i) for (i,_) in optstrs])+2
    hlp_len = max_len - opt_len
    
    out = []
    for (opt,hlp) in optstrs:
        out.append(opt.ljust(opt_len) + hlp[:hlp_len])
        while True:
            hlp = hlp[hlp_len:]
            if len(hlp) == 0: break
            out.append(''.ljust(opt_len)+hlp[:hlp_len])
    
    return '\n'.join(out)

def is_windows():
    '''Indicates we're running on a Windows system.
    
    Where possible, it's better to use capability tests a la
    http://www.alistapart.com/articles/testdriven
    however where it simply makes sense to differentiate between
    Windows and other OSs, this method is acceptable.'''
    return os.name == 'nt'

def system(cmd, environ={}, cwd=None, onerr=None, errprefix=None, out=None):
    '''enhanced shell command execution.
    run with environment maybe modified, maybe in different dir.

    if command fails and onerr is None, return status.  if ui object,
    print error message and return status, else raise onerr object as
    exception.

    if out is specified, it is assumed to be a file-like object that has a
    write() method. stdout and stderr will be redirected to out.
    
    From Mercurial's util.py'''
    try:
        sys.stdout.flush()
    except Exception:
        pass
    def py2shell(val):
        'convert python object into string that is useful to shell'
        if val is None or val is False:
            return '0'
        if val is True:
            return '1'
        return str(val)
    origcmd = cmd
    env = dict(os.environ)
    env.update((k, py2shell(v)) for k, v in environ.items())
    if out is None:
        rc = subprocess.call(cmd, shell=True, env=env, cwd=cwd)
    else:
        proc = subprocess.Popen(cmd, shell=True, env=env, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            out.write(line)
        proc.wait()
        rc = proc.returncode
    if rc and onerr:
        errmsg = '%s %s' % (os.path.basename(origcmd.split(None, 1)[0]),
                            "Failed to execute subprocess.")
        if errprefix:
            errmsg = '%s: %s' % (errprefix, errmsg)
        raise onerr(errmsg)
    return rc

class Timer:
    '''A simple runtime-timer to track how long given processes take.
    
    Note that attempting to repr() or str() this class without calling stop()
    will stop the Timer, and that a stopped timer cannot be restarted.
    If you want to time how long an operation takes, start your Timer, ignore it,
    then print the Timer.  If you need more granular measurements, use multiple
    Timers, or implement something else, Timer isn't what you're looking for.'''
    def __init__(self,desc,pattern="Timer: %s took %f",use_clock=False):
        self.pattern = pattern
        self.desc = desc
        self.use_clock = use_clock or is_windows()
        self.stopped = False
        
        self.time = time.time()
        self.clock = time.clock()
    
    def stop(self):
        times = (time.time(),time.clock())
        
        # We check stopped after making time calls to minimize time taken by Timer class
        if self.stopped:
            raise error.SeriousAbort("Called Timer.stop() more than once.")
        else:
            self.stopped = True
        
        self.time = times[0] - self.time
        self.clock = times[1] - self.clock
        
        return self.duration()
    
    def duration(self):
        if self.stopped:
            return self.clock if self.use_clock else self.time
        else:
            if self.use_clock:
                return time.clock() - self.clock
            else:
                return time.time() - self.time
    
    def __repr__(self):
        try:
            self.stop()
        except: pass
        return '(%f, %f)' % (self.time, self.clock)
    
    def __str__(self):
        try:
            self.stop()
        except: pass
        return self.pattern % (self.desc, self.clock if self.use_clock else self.time)

_ab_pat = re.compile(r'\s*AB:.*')
def ab_strip(lines):
    '''Used to process files containing input from the user.
    
    Given an iterator of strings, returns an iterator of those
    strings which do not start with "AB:"'''
    for line in lines:
        if not _ab_pat.match(line):
            yield line

_bracket_pat = re.compile(r'^\s*\[.+\]\s*$')
def bracket_strip(lines):
    '''Used to process files containing input from the user.
    
    Given an iterator of strings containing sections delimited by
    strings starting with bracketed text (like "[section]") return
    a list of the text in each section.  Note that index 0 of the
    list is any content before the first section.'''
    secs = []
    sec = []
    for line in lines:
        if _bracket_pat.match(line):
            secs.append(''.join(sec).strip())
            sec = []
        else:
            sec.append(line)
    secs.append(''.join(sec).strip())
    return secs