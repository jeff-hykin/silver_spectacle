import json_fix
import json

def Track(value):
    value = json.loads(json.dumps(value))
    if isinstance(self.value, list):
        return TrackedList(value)
    elif isinstance(self.value, dict):
        return TrackedDict(value)
    else:
        value

class TrackedData:
    self.is_deleted = False
    self.listeners = []
    def add_change_listener(self, a_function):
        self.listeners.append(a_function)
    
class TrackedList(TrackedData):
    def __init__(self, value):
        self.value = []
        self.is_deleted = False
        for index, each in enumerate(value):
            each = Track(each)
            if isinstance(each, TrackedData):
                self.value.append(each)
                # change(value=, keylist=, action=, args=)
                each.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "keylist": [index]+kwargs.get("keylist",[])}) )
    
    def _change_from(self, **kwargs):
        if self.is_deleted:
            return # do nothing
        
        for each in self.listeners:
            each({
                **dict(keylist=[]),
                **kwargs,
                **dict(value=self.value),
            })
    
    def splice(self, start, end=None, new_values=[]):
        if start < 0:
            start = len(self.value) + start
        if type(end) == type(None):
            end = len(self.values)
        if end < 0:
            end = len(self.value) + end
        front  = self.value[     : start]
        middle = self.value[start: end  ]
        back   = self.value[end  :      ]
        self.value = front+[ Track(each) for each in new_values ]+back
        if not self.is_deleted:
            for each in self.listeners:
                each(value=self, keylist=[], action="splice", args=[start, end, new_values])
        
        for each in middle:
            if isinstance(each, TrackedData):
                each.is_deleted = True
        
        return json.loads(json.dumps(middle))
    
    def __getitem__(self, index):
        return self.value[index]
        
    def __setitem__(self, index, value):
        self.splice(index, index+1, [value])
    
    def __delitem__(self, index):
        self.splice(index, index+1)
    
    def __len__(self):
        return len(self.value)
    
    def __json__(self):
        return self.value
    
    def __contains__(self,   *args, **kwargs): return self.value.__contains__(*args, **kwargs)
    def __iter__(self, *args, **kwargs): return self.value.__iter__(*args, **kwargs)
    def __repr__(self, *args, **kwargs): return self.value.__repr__(*args, **kwargs)
    def __str__(self,  *args, **kwargs): return self.value.__str__(*args, **kwargs)
    def __eq__(self,   *args, **kwargs): return self.value.__eq__(*args, **kwargs)
    
    def __add__(self, other_list):
        self.splice(len(self.value), len(self.value), list(other_list))
    
    def append(self, value):
        self.splice(len(self.value), len(self.value), [value])
    
    def clear(self, value):
        self.splice(0, len(self.value), [])
    
    def copy(self):
        return self.value
    
    def count(self, item):
        return self.value.count(item)
    
    def extend(self, other_list):
        self.splice(len(self.value), len(self.value), list(other_list))
    
    def index(self, item):
        return self.index(item)
    
    def insert(self, index, object):
        self.splice(index,index, object)
    
    def pop(self, index=-1):
        self.splice(index, index+1)
    
    def remove(self, value):
        if value in self.values:
            index = self.index(value)
            self.splice(index, index+1)
    
    def reverse(self):
        copy = list(self.value)
        self.value.reverse()
        # only update if necessary
        if copy != self.value: 
            self.splice(0, len(self.value), self.value)
    
    def sort(self, *, key=None, reverse=False):
        copy = list(self.value)
        self.value.sort(key=None, reverse=False)
        # only update if necessary
        if copy != self.value: 
            self.splice(0, len(self.value), self.value)

class TrackedDict(TrackedData):
    pass

class Card:
    def __init__(self, update_function, **kwargs):
        self.id = id(self)
        self.timeline = []
        self.initial_data = kwargs
        self.update_function = update_function # javascript string
    
    
    def _as_html_(self):
        return ""
    
    def save(path):
        # convers self to HTML then saves that as a file
        # TODO: force existance of path
        with open(path, 'w') as the_file:
            the_file.write(str(self._as_html_()))