import json_fix
import json
from time import time as now

unix_epoch = lambda : now()/1000

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
    def _got_deleted(self):
        self.is_deleted = True
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
                # change(value=, path=, action=, args=, time=)
                each.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [index]+kwargs.get("path",[])}) )
    
    def _got_deleted(self):
        self.is_deleted = True
        for each in self.value:
            if isinstance(each, TrackedData):
                each._got_deleted()
    
    def _change_from(self, **kwargs):
        if self.is_deleted:
            return # do nothing
        
        for each in self.listeners:
            each({
                **dict(path=[]),
                **kwargs,
                **dict(value=self.value),
            })
    
    # minimum-spanning-method 1 of 1
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
                each(value=self, path=[], action="splice", args=json.loads(json.dumps([start, end, new_values])), time=unix_epoch())
        
        for each in middle:
            if isinstance(each, TrackedData):
                each.is_deleted = True
                # change(value=, path=, action=, args=)
                each.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [index]+kwargs.get("path",[])}) )
        
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
    def __reversed__(self, *args, **kwargs): return self.value.__reversed__(*args, **kwargs)
    
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
    def __init__(self, value):
        self.value = {}
        self.is_deleted = False
        for key, each_value in enumerate(value):
            each_value = Track(each_value)
            if isinstance(each_value, TrackedData):
                self.each_value.append(each_value)
                # change(value=, path=, action=, args=)
                each_value.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [key]+kwargs.get("path",[])}) )
    
    def _change_from(self, **kwargs):
        if self.is_deleted:
            return # do nothing
        
        for each in self.listeners:
            each({
                **dict(path=[]),
                **kwargs,
                **dict(value=self.value),
            })
    
    def _got_deleted(self):
        self.is_deleted = True
        for each in self.value.values():
            if isinstance(each, TrackedData):
                each._got_deleted()
    
    # minimum-spanning-method 1 of 2
    def delete(self, *keys):
        for key in keys:
            if isinstance(self.value[key], TrackedData):
                self.value[key].is_deleted = True
            del self.value[key]
        if not self.is_deleted:
            for each in self.listeners:
                each(value=self, path=[], action="delete", args=list(keys), time=unix_epoch())
    
    # minimum-spanning-method 2 of 2
    def merge(self, other_dict, **kwargs):
        other_dict = dict(other_dict)
        other_dict.update(kwargs)
        
        for each_key, each_value in other_dict.items():
            self.value[each_key] = Track(each_value)
        
        if not self.is_deleted:
            for each_key, each_value in other_dict.items():
                if isinstance(self.value[each_key], TrackedData):
                    each_value.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [each_key]+kwargs.get("path",[])}) )
        
            for each in self.listeners:
                each(value=self, path=[], action="merge", args=json.loads(json.dumps([other_dict])), time=unix_epoch())
        
        return self
    
    # basically inherit
    def __getitem__ (self, *args, **kwargs): return self.value.__getitem__ (*args, **kwargs)
    def __len__     (self, *args, **kwargs): return self.value.__len__     (*args, **kwargs)
    def __contains__(self, *args, **kwargs): return self.value.__contains__(*args, **kwargs)
    def __iter__    (self, *args, **kwargs): return self.value.__iter__    (*args, **kwargs)
    def __repr__    (self, *args, **kwargs): return self.value.__repr__    (*args, **kwargs)
    def __str__     (self, *args, **kwargs): return self.value.__str__     (*args, **kwargs)
    def __eq__      (self, *args, **kwargs): return self.value.__eq__      (*args, **kwargs)
    def __reversed__(self, *args, **kwargs): return self.value.__reversed__(*args, **kwargs)
    def get   (self, *args, **kwargs): return self.value.get   (*args, **kwargs)
    def values(self, *args, **kwargs): return self.value.values(*args, **kwargs)
    def items (self, *args, **kwargs): return self.value.items (*args, **kwargs)
    def keys  (self, *args, **kwargs): return self.value.keys  (*args, **kwargs)
    
    # minimal changes
    def __json__(self, ): return self.value
    def __add__(self, other_dict): self.merge(other_dict)
    def __setitem__(self, key, value): self.merge({key:value})
    def __delitem__(self, key): self.delete(key)
    
    # 
    # methods
    # 
    def update(self, iterable, **kwargs):
        other_dict = {}
        if not hasattr(iterable, "keys") or not callable(iterable.keys):
            for k, v in iterable:
                other_dict[k] = v
        self.merge(other_dict, **kwargs)
        
    def clear(self):
        # delete all the keys
        self.delete(*tuple(self.values.keys()))
    
    def copy(self):
        return dict(self.value)
    
    def fromkeys(self, iterable, value=None):
        new_items = { key:value for key in iterable }
        self.merge(new_items)
    
    def pop(self, k, d=None):
        if k not in self.value:
            return d
        else:
            value = self.value[k]
            del self[k]
            return value
    
    def popitem(self):
        removed_key, removed_value = self.value.popitem()
        self.value[removed_key] = removed_value
        del self.value[removed_key]
        return removed_key, removed_value
        
    def setdefault(self, key, default=None):
        if key not in self.value:
            self.merge({ key: default})
        return self.get(key, default)

class Card:
    associated_runtime = now()
    
    def __init__(self, update_function, **kwargs):
        self.id = id(self)
        self.timeline = []
        self.data = Track(kwargs)
    
    def _as_js_(self):
        # should change as self.data changes
        return """function ({id, data}) {
            const runtimeData = {}
            const element = document.createElement("div")
            element.onDataChange = function({ value, path, action, args, time }) {
                // change the element somehow when the data changes
            }
            return element
        }"""
    
    def save(path):
        # converts self to HTML then saves that as a file
        # TODO: force existance of path
        with open(path, 'w') as the_file:
            the_file.write(str(self._as_html_()))