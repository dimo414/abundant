# Copyright 2011 Michael Diamond
# 
# This file is part of Abundant.
# 
# This software may be used and distributed according to the terms of
# the  GNU General Public License version 3 or any later version.
# See http://www.gnu.org/licenses/ for the full license text.

'''
@author: Michael Diamond
Created on Feb 2, 2011
'''

import json,os,time

from abundant import error,util

class Issue:
    '''
    This class represents the Issue data structure, and notably is responsible
    for serializing and unserializing it in a safe way.  No other modules should
    read or write the bug files directly.
    
    When working with an issue, it is important to remember that almost all data
    is optional, and defaults to None or the empty list.  In general, data without
    values should be hidden from the user as if it didn't exist at all.
    '''
    
    # display strings for issue components 
    _pretty = {'id':"ID",
                 'parent':"Parent", 'children':"Children", 'duplicates':"Duplicates",
                 'creator':"Creator", 'assigned_to':"Assigned To", 'listeners':"Listeners",
                 'issue':"Issue Type", 'target':"Target", 'severity':"Severity", 'status':"Status",
                        'resolution':"Resolution", 'category':"Category",
                 'creation_date':"Created", 'resolved_date':"Resolved", 'projection':"Projection",
                        'estimate':"Estimate",
                 'title':"Title", 'paths':"Paths", 'description':"Description",'reproduction':"Reproduction Steps",
                        'expected':"Expected Result", 'trace':"Stack Trace",
                 'comments':"Comments"
               }
    # display order of issue components, since they're stored in a dict
    _order = ['id','parent','children','duplicates',
              'creator','assigned_to','listeners',
              'issue','target','severity','status','resolution','category',
              'creation_date','resolved_date','projection','estimate',
              'title','paths','description','reproduction','expected','trace','comments']
    # issue data that are IDs
    _ids = set(['id','parent','children','duplicates'])
    # issue data that are dates
    _dates = set(['creation_date','resolved_date'])
    # issue data that is likely to be multi-line
    _long = set(['listeners','paths','description','reproduction','expected','trace','comments'])
    

    def __init__(self,
                 id=None,
                 parent=None, children=None, duplicates=None,
                 creator=None, assigned_to=None, listeners=None,
                 issue=None, target=None, severity=None, status=None, resolution=None, category=None,
                 creation_date=None, resolved_date=None, projection=None, estimate=None,
                 title=None, paths=None, description=None, reproduction=None, expected=None, trace=None,
                 comments=None):
        '''
        The issue constructor takes any of the data that an issue consists of.  (Almost)
        all of the fields are optional.
        
        If an ID is not specified, the issue is considered a new issue, and an ID is generated
        from the title, creation date, and creator, if one exists.  If a creation date is not
        specified, the current system time is used.
        
        If an ID is specified, the issue is considered a preexisting issue, and all other data
        points are left alone.
        
        These two cases guarantee the id attribute will always have a value.  It would be unwise
        to modify this value.
        '''
        self.id = id
        # Relations
        self.parent = parent
        self.children = children if children else []
        self.duplicates = duplicates
        # Users
        self.creator = creator
        self.assigned_to = assigned_to
        self.listeners = listeners if listeners else []
        # Status
        self.issue = issue
        self.target = target
        self.severity = severity
        self.status = status
        self.resolution = resolution
        self.category = category
        # Times
        self.creation_date = creation_date
        self.resolved_date = resolved_date
        self.projection = projection
        self.estimate = estimate
        # Data
        self.title = title
        self.paths = paths if paths else []
        self.description = description
        self.reproduction = reproduction
        self.expected = expected
        self.trace = trace
        self.comments = comments if comments else []
        
        #new issue
        if self.id == None and self.creation_date == None:
            self.creation_date = time.time();
            self.id = util.hash(repr(self.creation_date)+
                                (self.title if self.title else '')+
                                (self.creator if self.creator else ''))
    
    def pretty(self,key):
        return self._pretty[key]
    
    def filename(self):
        ''' Returns the suggested filename for this issue '''
        return self.id+ext
    
    def to_JSON(self, path, file=None):
        ''' Converts the issue to a JSON datastructure and writes it
        to the specified path and file.
        '''
        if file == None:
            file = self.filename()
        dict = {}
        for k, v in self.__dict__.items():
            if(v != None and v != []):
                dict[k] = v
        json.dump(dict,open(os.path.join(path,file),'w'),
                  indent=1,sort_keys=True)
        
    def details(self, ui=None, db=None, skip=[]):
        out = []
        for key in self._order:
            if key not in skip:
                val = self.__dict__[key]
                if val is None or val == []:
                    continue
                
                if db is not None and key in self._ids:
                    if isinstance(val,list):
                        val = [db.iss_prefix.pref_str(i,True) for i in val]
                    else: val = db.iss_prefix.pref_str(val,key!='id')
                if key == 'comments':
                    val = [comment_to_str(i,ui) for i in val]
                if ui is not None and key in self._dates:
                    val = ui.to_long_time(val)
                
                str = "%s:%s%s" % (self.pretty(key),
                                   "\n" if key in self._long else " ",
                                   util.list2str(val, key in self._long)) 
                
                out.append(str)
        return '\n'.join(out)
    
    def diff(self, iss):
        '''Returns the difference of two issues.
        See util.diff_dict for the expected structure
        of the returned data.'''
        return util.diff_dict(self.__dict__,iss.__dict__)
    
    def descChanges(self, iss, ui=None, skip=['id']):
        '''Returns a structured string describing the changes
        between two issues.'''
        diff = self.diff(iss)
        out = []
        
        def arc(key,word,diff,pad='  '):
            if key not in diff: return ''
            
            now, was = diff[key]
            
            if ui is not None and key in self._dates:
                now = ui.to_short_time(now)
                was = ui.to_short_time(was)
        
            if(isinstance(now,list) or isinstance(was,list)):
                if now is None: now = []
                if was is None: was = []
                str = pad
                if len(now) > 0:
                    str += "Added %s to %s" % (util.list2str(now),word)
                if len(now) > 0 and len(was) > 0:
                    str += ", "
                if len(was) > 0:
                    str += "Removed %s" % util.list2str(was)
                    if len(now) == 0:
                        str += " from %s" % word
                return str
            
            if now == None:
                return "%sRemoved %s, was %s" % (pad,word,was)
            else:
                str = "%sSet %s to %s" % (pad,word,now)
                if was != None:
                    str = "%s, was %s" % (str,was)
                return str
        
        # construct list of strings then join
        # http://www.skymind.com/~ocrow/python_string/
        
        for key in self._order:
            if key not in skip:
                out.append(arc(key,self.pretty(key),diff))
        return '\n'.join(filter((lambda x : x.strip() != ''),out))

def comment_to_str(com,ui=None):
    ret = "%s\n\nAt %s" % (com[2],ui.to_short_time(com[1]) if ui else com[1])
    if com[0]:
        return ret + " by %s" % com[0]
    return ret
    
def JSON_to_Issue(file):
    ''' Constructs a new issue from JSON data in the
    specified file '''
    try:
        return Issue(**json.load(open(file)))
    except IOError:
        raise error.NoSuchIssue("No issue could be found at: \n  %s" % file)
    except ValueError:
        raise error.InvalidIssue("Invalid issue file at: \n  %s" % file)


ext = ".issue"

#Constructs an identity issue to compare
#others against for changes'''
base = Issue()

# unit test on bug reading and writing
if __name__ == '__main__':
    dir = '.'
    issue = Issue(title="This is a test")
    issue.to_JSON(dir)
    issue2 = JSON_to_Issue(os.path.join(dir,issue.filename()))
    if sum([len(s) for s in issue.diff(issue2)]) == 0:
        print("Read and write looks good")
    else:
        print("Something's wrong, different structure after read/write")
        print("Diff:",issue.diff(issue2))
    os.remove(issue.filename())
    print("Diff of issue with base:",issue.diff(base))