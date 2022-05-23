import json_fix
import json
from time import time as now
from blissful_basics import print, flatten, to_pure, stringify, stats, product, countdown, is_generator_like, now, large_pickle_save, large_pickle_load, FS, Object
from super_hash import super_hash
from runtime_setup import server
from random import random

unix_time = lambda : int(now()/1000)

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
                each(value=self, path=[], action="splice", args=json.loads(json.dumps([start, end, new_values])), time=unix_time())
        
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
        self._change_indicator = random()
        for key, each_value in enumerate(value):
            each_value = Track(each_value)
            if isinstance(each_value, TrackedData):
                self.each_value.append(each_value)
                # change(value=, path=, action=, args=)
                each_value.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [key]+kwargs.get("path",[])}) )
    
    def _change_from(self, **kwargs):
        if self.is_deleted:
            return # do nothing
        
        self._change_indicator = random()
        for each in self.listeners:
            each({
                **dict(path=[]),
                **kwargs,
                **dict(value=self.value),
            })
    
    def _got_deleted(self):
        self.is_deleted = True
        self._change_indicator = random()
        for each in self.value.values():
            if isinstance(each, TrackedData):
                each._got_deleted()
    
    # minimum-spanning-method 1 of 2
    def delete(self, *keys):
        for key in keys:
            if isinstance(self.value[key], TrackedData):
                self.value[key].is_deleted = True
                self.value[key]._got_deleted()
            del self.value[key]
        if not self.is_deleted:
            self._change_indicator = random()
            for each in self.listeners:
                each(value=self, path=[], action="delete", args=list(keys), time=unix_time())
    
    # minimum-spanning-method 2 of 2
    def merge(self, other_dict, **kwargs):
        other_dict = dict(other_dict)
        other_dict.update(kwargs)
        
        for each_key, each_value in other_dict.items():
            self.value[each_key] = Track(each_value)
        
        if not self.is_deleted:
            self._change_indicator = random()
            for each_key, each_value in other_dict.items():
                if isinstance(self.value[each_key], TrackedData):
                    each_value.listeners.append(lambda **kwargs: self._change_from(**{**kwargs, "path": [each_key]+kwargs.get("path",[])}) )
        
            for each in self.listeners:
                each(value=self, path=[], action="merge", args=json.loads(json.dumps([other_dict])), time=unix_time())
        
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

class Frontend:
    def __init__(self, title=None):
        self.title = title
        self.spectacle_classes = {}
        self.spectacles = {}
        self._html_cache = None
        self._html_change_indicator = None
        # FIXME: contact the server to create a new frontend page
    
    def add(self, *spectacles):
        for each in spectacles:
            self.spectacle_classes[each.class_id] = each
            self.spectacles[f'{each.instance_id}{each.class_id}'] = each
        return self
    
    def _get_html_change_indicator(self):
        change_indicator = ""
        for full_id, each_value in self.spectacles.items():
            change_indicator += f"{full_id}{each_value.data._change_indicator}"
        return super_hash(change_indicator)
    
    @property
    def as_html(self):
        if self._html_cache and self._get_html_change_indicator() == self._html_change_indicator:
            return self._html_cache
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title></title>
                <style>
                        /* 

                        Baseline CSS 3

                        */

                        @-ms-viewport {
                            width: device-width;
                        }
                        article, aside, details, figcaption, figure, footer, header, hgroup, menu, nav, section, main, summary {
                            display: block;
                        }

                        *, *::before, *::after {
                            box-sizing: inherit;
                        }

                        html {
                            /* 1 */
                            box-sizing: border-box;
                            /* 2 */
                            touch-action: manipulation;
                            /* 3 */
                            -webkit-text-size-adjust: 100%;
                            -ms-text-size-adjust: 100%;
                            /* 4 */
                            -ms-overflow-style: scrollbar;
                            /* 5 */
                            -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
                        }

                        body {
                            line-height: 1;
                        }

                        html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, time, mark, audio, video, main {
                            font-size: 100%;
                            font: inherit;
                            vertical-align: baseline;
                        }

                        ol, ul {
                            list-style: none;
                        }

                        blockquote, q {
                            quotes: none;
                        }

                        blockquote::before, blockquote::after, q::before, q::after {
                            content: "";
                            content: none;
                        }

                        table {
                            border-collapse: collapse;
                            border-spacing: 0;
                        }

                        hr {
                            /* 1 */
                            box-sizing: content-box;
                            height: 0;
                            /* 2 */
                            overflow: visible;
                        }

                        pre, code, kbd, samp {
                            /* 1 */
                            font-family: monospace, monospace;
                        }

                        pre {
                            /* 2 */
                            overflow: auto;
                            /* 3 */
                            -ms-overflow-style: scrollbar;
                        }

                        a {
                            /* 1 */
                            background-color: transparent;
                            /* 2 */
                            -webkit-text-decoration-skip: objects;
                        }

                        abbr[title] {
                            /* 1 */
                            border-bottom: none;
                            /* 2 */
                            text-decoration: underline;
                            text-decoration: underline dotted;
                        }

                        b, strong {
                            font-weight: bolder;
                        }

                        small {
                            font-size: 80%;
                        }

                        sub, sup {
                            font-size: 75%;
                            line-height: 0;
                            position: relative;
                        }

                        sub {
                            bottom: -0.25em;
                        }

                        sup {
                            top: -0.5em;
                        }

                        img {
                            border-style: none;
                        }

                        svg:not(:root) {
                            overflow: hidden;
                        }

                        button {
                            border-radius: 0;
                        }

                        input, button, select, optgroup, textarea {
                            font-family: inherit;
                            font-size: inherit;
                            line-height: inherit;
                        }

                        button, [type=reset], [type=submit], html [type=button] {
                            -webkit-appearance: button;
                        }

                        input[type=date], input[type=time], input[type=datetime-local], input[type=month] {
                            -webkit-appearance: listbox;
                        }

                        fieldset {
                            min-width: 0;
                        }

                        [tabindex="-1"]:focus {
                            outline: 0 !important;
                        }

                        button, input {
                            overflow: visible;
                        }

                        button, select {
                            text-transform: none;
                        }

                        button::-moz-focus-inner, [type=button]::-moz-focus-inner, [type=reset]::-moz-focus-inner, [type=submit]::-moz-focus-inner {
                            border-style: none;
                            padding: 0;
                        }

                        legend {
                            /* 1 */
                            max-width: 100%;
                            white-space: normal;
                            /* 2 */
                            color: inherit;
                            /* 3 */
                            display: block;
                        }

                        progress {
                            vertical-align: baseline;
                        }

                        textarea {
                            overflow: auto;
                        }

                        [type=checkbox], [type=radio] {
                            /* 1 */
                            box-sizing: border-box;
                            /* 2 */
                            padding: 0;
                        }

                        [type=number]::-webkit-inner-spin-button, [type=number]::-webkit-outer-spin-button {
                            height: auto;
                        }

                        [type=search] {
                            /* 1 */
                            -webkit-appearance: textfield;
                            /* 2 */
                            outline-offset: -2px;
                        }

                        [type=search]::-webkit-search-cancel-button, [type=search]::-webkit-search-decoration {
                            -webkit-appearance: none;
                        }

                        ::-webkit-file-upload-button {
                            /* 1 */
                            -webkit-appearance: button;
                            /* 2 */
                            font: inherit;
                        }

                        template {
                            display: none;
                        }

                        [hidden] {
                            display: none;
                        }

                        button:focus {
                            outline: 1px dotted;
                            outline: 5px auto -webkit-focus-ring-color;
                        }

                        button:-moz-focusring, [type=button]:-moz-focusring, [type=reset]:-moz-focusring, [type=submit]:-moz-focusring {
                            outline: 1px dotted ButtonText;
                        }

                        html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, time, mark, audio, video, main {
                            margin: 0;
                            padding: 0;
                            border: 0;
                        }

                        input, button, select, optgroup, textarea {
                            margin: 0;
                        }

                        body {
                            width: 100vw;
                            min-height: 100vh;
                            overflow: visible;
                            scroll-behavior: auto;
                        }

                        textarea {
                            resize: vertical;
                        }

                        br {
                            display: block;
                            content: "";
                            border-bottom: 0px solid transparent;
                        }

                        h1 {
                            font-size: 2.78rem;
                        }

                        h2 {
                            font-size: 2.454rem;
                        }

                        h3 {
                            font-size: 2.128rem;
                        }

                        h4 {
                            font-size: 1.802rem;
                        }

                        h5 {
                            font-size: 1.476rem;
                        }

                        h6 {
                            font-size: 1.15rem;
                        }

                        body {
                            font-family: sans-serif;
                        }

                        :root {
                            --css-baseline-scrollbar-background: lightgray;
                            --css-baseline-scrollbar-foreground: dimgray;
                        }

                        * {
                            scrollbar-color: var(--css-baseline-scrollbar-foreground) var(--css-baseline-scrollbar-background);
                        }

                        *::-webkit-scrollbar {
                            width: 10px;
                        }

                        *::-webkit-scrollbar-track {
                            background: var(--css-baseline-scrollbar-background);
                        }

                        *::-webkit-scrollbar-thumb {
                            background-color: var(--css-baseline-scrollbar-foreground);
                            border: 2px solid var(--css-baseline-scrollbar-background);
                            border-radius: 20px;
                        }
                </style>
                <style>
                    @keyframes silver-spectacle-loader-dash {
                        0% {
                            stroke-dasharray: 1, 95;
                            stroke-dashoffset: 0;
                        }
                        50% {
                            stroke-dasharray: 85, 95;
                            stroke-dashoffset: -25;
                        }
                        100% {
                            stroke-dasharray: 85, 95;
                            stroke-dashoffset: -93;
                        }
                    }
                    @keyframes silver-spectacle-loader-rotate {
                        0% {
                            transform: rotate(0deg);
                        }
                        100% {
                            transform: rotate(360deg);
                        }
                    }
                </style>
            </head>
            <body>
                <div id="silver-spectacle-initial-loader" style="position: fixed; top: 0; left: 0px; z-index: 1100; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: block; -webkit-transition: ease-in-out 0.1s; -moz-transition: ease-in-out 0.1s; -o-transition: ease-in-out 0.1s; -ms-transition: ease-in-out 0.1s; transition: ease-in-out 0.1s; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing: border-box; " >
                    <span style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing: border-box; display: block; width: 48px; height: 48px; padding: 4px; background-color: #ffffff; -webkit-border-radius: 100%; -moz-border-radius: 100%; -o-border-radius: 100%; -ms-border-radius: 100%; border-radius: 100%; position: absolute; left: 50%; margin-left: -24px; top: -50px; -webkit-transition: ease-in-out 0.1s; -moz-transition: ease-in-out 0.1s; -o-transition: ease-in-out 0.1s; -ms-transition: ease-in-out 0.1s; transition: ease-in-out 0.1s; -webkit-box-shadow: #000 0px 5px 10px -5px; -moz-box-shadow: #000 0px 5px 10px -5px; -o-box-shadow: #000 0px 5px 10px -5px; -ms-box-shadow: #000 0px 5px 10px -5px; box-shadow: #000 0px 5px 10px -5px; top: 18%;" >
                        <svg width="40" height="40" version="1.1" xmlns="http://www.w3.org/2000/svg" style="overflow: hidden; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; -o-box-sizing: border-box; -ms-box-sizing: border-box; box-sizing: border-box; width: 40; height: 40; fill: transparent; stroke: #1a73e8; stroke-width: 5; animation: silver-spectacle-loader-dash 2s ease infinite, silver-spectacle-loader-rotate 2s linear infinite;">
                            <circle cx="20" cy="20" r="15">
                        </svg>
                    </span>
                </div>
            </body>
        """
        
        # spectacle classes/library setup
        for each_key, each_value in self.spectacle_classes.items():
            html += each_value.style + "\n" + each_value.script + "\n"
        
        # spectacle instances
        all_instances = """
            <script>
                import { silverSpectacle } from "https://deno.land/x/silver_spectacle@0.0.1/main.js"
        """
        # function to handle recursion
        def create_children(each_value):
            code = ""
            for each in each_value.nested_spectacles:
                # recursive (basecase = nested_spectacles is empty)
                code += create_children(each_value) + """
                    silverSpectacle.createSpectacle({
                        spectacleClassId: '"""+each_value.class_id+"""',
                        instanceId: '"""+each_value.instance_id+"""',
                        topLevel: false,
                        useDefaultContainer: false,
                        data: """+json.dumps(each_value.data)+""",
                    })
                """
        
        for each_key, each_value in self.spectacles.items():
            try:
                # do nested ones first
                all_instances += create_children(each_value.nested_spectacles)
                # top level ones are the only one
                all_instances += """
                    silverSpectacle.createSpectacle({
                        spectacleClassId: '"""+each_value.class_id+"""',
                        instanceId: '"""+each_value.instance_id+"""',
                        topLevel: true,
                        useDefaultContainer: """+("true" if each.use_default_container else "false")+""",
                        data: """+json.dumps(each_value.data)+""",
                    })
                """
            except Exception as error:
                pass
        all_instances += """
            silverSpectacle.renderAll()
        """
        html += all_instances+"            </script>\n</html>"
        self._html_cache = html
        return html
    
    def save(self, path):
        FS.write(data=self.as_html, to=path)

class_id_helper = Object(current_id=unix_time())
def Spectacle(*args, **kwargs):
    """
    @Spectacle()
    class YourChart:
        script = '''<script>
            ...
            let class_id = "'''+Spectacle.get_class_id()+'''"
            ...
        </script>'''
    """
    
    def class_wrapper(class_being_wrapped)
        # 
        # class properties
        # 
        class_being_wrapped.class_id = class_id_helper.current_id
        if not hasattr(class_being_wrapped, 'style'):
            class_being_wrapped.style = """<style>
                /* css styles go here */
            </style>"""
        
        if not hasattr(class_being_wrapped, 'script'):
            raise Exception('''
            
                The class '''+str(class_being_wrapped)+''' doesn't have a `script` attribute, please make sure to define one
                Example:
                    @Spectacle()
                    class '''+str(class_being_wrapped.__name__)+''':
                        script = """<script>
                            import { silverSpectacle } from "https://deno.land/x/silver_spectacle@0.0.1/main.js"
                            import { Elemental } from "https://deno.land/x/elementalist@0.0.14/main/main.mjs"
                            let html = Elemental() // see: https://deno.land/x/elementalist
                        
                            const elements = {}
                            silverSpectacle.register({
                                spectacleClassId: """+f'"{Spectacle.get_class_id()}"'+""",
                            
                                // create an element
                                async init({instanceId, data}) {
                                    elements[instanceId] = html`<div> replace me with stuff </div>`
                                
                                    // return an html element
                                    return elements[instanceId]    
                                },
                                
                                // change the element when data changes
                                async onDataChange({ instanceId, value, path, action, args, time }) {
                                    // change the element somehow when the data changes
                                    const element = elements[instanceId]
                                }
                            })
                        </script>"""
                        
                        def __init__(self, arg1_data):
                            self.data["arg1_data"] = arg1_data
            ''')
        
        # 
        # __init__
        # 
        original_init = class_being_wrapped.__init__
        def new_init(self, *args, **kwargs):
            self.instance_id = unix_time()
            self.class_id = class_being_wrapped.class_id
            self.timeline = []
            self.data = Track({})
            self.nested_spectacles = []
            self.use_default_container = True
            output = original_init(self, *args, **kwargs)
            # ping the server with the inital data
            server_api.spectacle_init(class_id=self.class_id, instance_id=self.instance_id, value=self.data)
            # ping the server with every update
            self.data.listeners.append(lambda **kwargs: server_api.spectacle_update(**kwargs)) # kwargs=dict(value=, path=, action=, args=, time=)
            return output
        class_being_wrapped.__init__ = new_init
        
        # 
        # default methods
        # 
        if not hasattr(class_being_wrapped, "generate_html"):
            def generate_html(self):
                return Frontend().add(self).as_html
            class_being_wrapped.generate_html = generate_html
        
        if not hasattr(class_being_wrapped, "_repr_html_"):
            def _repr_html_(self, *args, **kwargs):
                return self.generate_html()
            class_being_wrapped._repr_html_ = _repr_html_
        
        if not hasattr(class_being_wrapped, "save"):
            def save(self, path):
                html = self.generate_html()
                FS.write(data=html, to=path)
            class_being_wrapped.save = save
        
        # end
        return class_being_wrapped
    
    return class_wrapper
# class-method-like
Spectacle.get_class_id = lambda: str(class_being_wrapped.class_id)