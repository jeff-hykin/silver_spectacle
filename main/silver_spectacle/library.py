import os
import requests
import subprocess
import time
import sys
import atexit


# 
# helper tools
# 

def _is_iterable(thing):
    # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    try:
        iter(thing)
    except TypeError:
        return False
    else:
        return True

def _to_pure(an_object, recursion_help=None):
    # 
    # infinte recursion prevention
    # 
    top_level = False
    if recursion_help is None:
        top_level = True
        recursion_help = {}
    class PlaceHolder:
        def __init__(self, id):
            self.id = id
        def eval(self):
            return recursion_help[key]
    object_id = id(an_object)
    # if we've see this object before
    if object_id in recursion_help:
        # if this value is a placeholder, then it means we found a child that is equal to a parent (or equal to other ancestor/grandparent)
        if isinstance(recursion_help[object_id], PlaceHolder):
            return recursion_help[object_id]
        else:
            # if its not a placeholder, then we already have cached the output
            return recursion_help[object_id]
    # if we havent seen the object before, give it a placeholder while it is being computed
    else:
        recursion_help[object_id] = PlaceHolder(object_id)
    
    parents_of_placeholders = set()
    
    # 
    # main compute
    # 
    return_value = None
    # base case 1 (iterable but treated like a primitive)
    if isinstance(an_object, str):
        return_value = an_object
    # base case 2 (exists because of scalar numpy/pytorch/tensorflow objects)
    elif hasattr(an_object, "tolist"):
        return_value = an_object.tolist()
    else:
        # base case 3
        if not _is_iterable(an_object):
            return_value = an_object
        else:
            if isinstance(an_object, dict):
                return_value = {
                    _to_pure(each_key, recursion_help) : _to_pure(each_value, recursion_help)
                        for each_key, each_value in an_object.items()
                }
            else:
                return_value = [ _to_pure(each, recursion_help) for each in an_object ]
    
    # convert iterables to tuples so they are hashable
    if _is_iterable(return_value) and not isinstance(return_value, dict) and not isinstance(return_value, str):
        return_value = tuple(return_value)
    
    # update the cache/log with the real value
    recursion_help[object_id] = return_value
    #
    # handle placeholders
    #
    if _is_iterable(return_value):
        # check if this value has any placeholder children
        children = return_value if not isinstance(return_value, dict) else [ *return_value.keys(), *return_value.values() ]
        for each in children:
            if isinstance(each, PlaceHolder):
                parents_of_placeholders.add(return_value)
                break
        # convert all the placeholders into their final values
        if top_level == True:
            for each_parent in parents_of_placeholders:
                iterator = enumerate(each_parent) if not isinstance(each_parent, dict) else each_parent.items()
                for each_key, each_value in iterator:
                    if isinstance(each_parent[each_key], PlaceHolder):
                        each_parent[each_key] = each_parent[each_key].eval()
                    # if the key is a placeholder
                    if isinstance(each_key, PlaceHolder):
                        value = each_parent[each_key]
                        del each_parent[each_key]
                        each_parent[each_key.eval()] = value
    
    # finally return the value
    return return_value

def _update_file(file_path, new_json_data):
    import json
    import shutil
    from os.path import join, isdir
    # make sure the parent exists
    try: os.makedirs(os.path.dirname(file_path))
    except:
        pass
    # read the existing data
    existing_data = {}
    try:
        with open(file_path, 'r') as in_file:
            existing_data = json.load(in_file)
    except Exception as error:
        pass
    
    new_json_data = {
        **new_json_data,
        **existing_data,
    }
    # try deleting whatever is in the way
    try:
        if isdir(file_path):
            shutil.rmtree(file_path)
        else:
            try: os.remove(file_path)
            except:
                pass
    except:
        pass
    
    # write the json
    with open(file_path, 'w') as outfile:
        json.dump(new_json_data, outfile)
    


# 
# 
# main code
# 
# 

_display_data = {}
_process = None
_settings = {
    "port": 9900,
    "server_start_timeout": 10,
    "custom_css": "",
    "custom_js": "",
}
def configure(**settings):
    global _settings
    _settings = {
        **_settings,
        **settings,
    }

def ensure_server_is_running():
    global _settings
    global _process
    port = _settings["port"]
    server_start_timeout = _settings["server_start_timeout"]
    result = None
    try:
        result = requests.get(f'http://localhost:{port}/ping')
    except Exception as error:
        pass
    # if no pong, then start the server and wait
    if not result or result.text != '"pong"':
        _process = subprocess.Popen(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "server.py"),
                "--port", str(_settings["port"]),
                "--custom-css", _settings["custom_css"],
                "--custom-js", _settings["custom_js"],
            ],
            stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
        )
        start = time.time()
        while not result or result.text != '"pong"':
            if time.time() - start > _settings["server_start_timeout"]:
                print(f"\n",  file=sys.stderr)
                print(f"[silver_spectacle] Tried to start a server on port {port}",  file=sys.stderr)
                print(f"[silver_spectacle] however after waiting {server_start_timeout} seconds ('server_start_timeout')",  file=sys.stderr)
                print(f"[silver_spectacle] the server failed to respond to ping requests",  file=sys.stderr)
                print(f"[silver_spectacle] no error will be thrown, but output likely will not be displayed",  file=sys.stderr)
                print(f"[silver_spectacle] {_process}",  file=sys.stderr)
                print(f"\n",  file=sys.stderr)
                break
            try:
                result = requests.get(f'http://localhost:{port}/ping')
            except Exception as error:
                pass
        # if started successfully
        if result and result.text == '"pong"':
            print(f"Server started at: http://0.0.0.0:{port}")
            
        return False
    else:
        return True

def display(system, *arguments):
    global _settings
    global _display_data
    port = _settings["port"]
    server_was_running = ensure_server_is_running()
    now = time.time()
    _display_data[str(int(now * 1000000000))] = {
        "time": now,
        "system": system,
        "arguments": arguments,
    }
    
    # remove complex classes in favor of simple lists/dicts (NOTE: doesn't remove recursive values)
    _display_data = _to_pure(_display_data)
    # send data and method
    response = requests.post(
        f'http://localhost:{port}/update',
        json=_display_data,
    )
    

# kill the server on exit, unless the data has not been viewed yet
@atexit.register
def check_on_server():
    result = None
    port = _settings["port"]
    try:
        result = requests.get(f'http://localhost:{port}/was_viewed')
    except Exception as error:
        pass
    # if the data has been viewed, then stop the server (data will still be available in browser)
    if result:
        if result.text == "true":
            _process and _process.kill()
        else:
            print('')
            print(f'There were unviewed results')
            print(f'So the display server is still running at: http://localhost:{port}')
            print(f'(use the stop server button to kill it now)')
            print('')
    else:
        # probably an old zombie process
        pass
    # if the user has not had time to load a web browser
    # then keep the server running so it's there when they do try to load it
    # FUTURE: give the web window a means of killing the server from there to prevent a zombie server process
        