import os
import requests
import subprocess
import time
import sys
import atexit


# 
# helper tools
# 

debugging = False

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

_card_data = {}
_process = None
_settings = {
    "port": 9900,
    "server_start_timeout": 10,
    "custom_css": "",
    "custom_js": "",
}

# in the future this will allow for non-local display servers
# however, for right now, silver_spectacle only officially supports localhost
def _get_base_url():
    user_provided_url = _settings.get("base_url", None)
    if isinstance(user_provided_url, str):
        return user_provided_url
    else:
        port = _settings["port"]
        return f"http://localhost:{port}"
    
def _contact_server(endpoint, data=None, catch_all_errors=False, ensure_server_is_up=True, bypass_purification=False):
    import json
    try:
        # remove complex classes in favor of simple lists/dicts (NOTE: doesn't remove recursive values)
        if not bypass_purification:
            data = _to_pure(data)
        if ensure_server_is_up:
            ensure_server_is_running()
        base_url = _get_base_url()
        response = requests.post(
            f'{base_url}/{endpoint}',
            json=data,
        )
        if response and isinstance(response.text, str):
            return json.loads(response.text)
        else:
            return None
    except Exception as error:
        if catch_all_errors:
            return None
        else:
            raise error

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
    result = _contact_server("ping", catch_all_errors=True, ensure_server_is_up=False)
    # if no pong, then start the server and wait
    if result != "pong":
        _process = subprocess.Popen(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "server.py"),
                "--port", str(_settings["port"]),
                "--custom-css", _settings["custom_css"],
                "--custom-js", _settings["custom_js"],
            ],
            **({} if debugging else dict(stdout=subprocess.PIPE)),
            # stderr=subprocess.STDOUT,
        )
        start = time.time()
        while result != "pong":
            if time.time() - start > _settings["server_start_timeout"]:
                print(f"\n",  file=sys.stderr)
                print(f"[silver_spectacle] Tried to start a server on port {port}",  file=sys.stderr)
                print(f"[silver_spectacle] however after waiting {server_start_timeout} seconds ('server_start_timeout')",  file=sys.stderr)
                print(f"[silver_spectacle] the server failed to respond to ping requests",  file=sys.stderr)
                print(f"[silver_spectacle] no error will be thrown, but output likely will not be displayed",  file=sys.stderr)
                print(f"[silver_spectacle] {_process}",  file=sys.stderr)
                print(f"\n",  file=sys.stderr)
                break
            result = _contact_server("ping", catch_all_errors=True, ensure_server_is_up=False)
        # if started successfully
        if result == "pong":
            address = _get_base_url()
            print(f"[silver_spectacle] server started at: {address}")
            
        return False
    else:
        return True

from collections import defaultdict
class DisplayCard:
    conversion_table = dict(
        init=defaultdict(lambda: {}),
        send=defaultdict(lambda: {}),
    )
    
    def __init__(self, interface, *arguments):
        global _card_data
        
        # 
        # first check the table for argument conversions
        # 
        kwargs = {}
        conversion_table = DisplayCard.conversion_table["init"][interface]
        for pattern, converter in reversed(conversion_table.items()):
            the_type_pattern_does_match = isinstance(pattern, type) and isinstance(arguments[0], pattern)
            the_callable_pattern_check_does_match = not isinstance(pattern, type) and callable(pattern) and pattern(arguments)
            if the_type_pattern_does_match or the_callable_pattern_check_does_match:
                arguments, kwargs = converter(*arguments)
                break
        
        self._interface = interface
        self._created_at = time.time()
        self.id = str(int(self._created_at * 1000000000))
        
        _card_data[self.id] = {
            "createdAt": self._created_at,
            "interface": interface,
            "arguments": arguments,
        }
        
        _contact_server("new_card", _card_data, bypass_purification=kwargs.get("bypass_purification", False))
    
    def _trigger(self, action, data, bypass_purification=False):
        return _contact_server("card_trigger", {
            "time": time.time(),
            "cardId": self.id,
            "action": action,
            "data": data,
        }, bypass_purification=bypass_purification)
    
    # send
    def send(self, data):
        kwargs = {}
        conversion_table = DisplayCard.conversion_table["send"][self._interface]
        for pattern, converter in reversed(conversion_table.items()):
            the_type_pattern_does_match = isinstance(pattern, type) and isinstance(data, pattern)
            the_callable_pattern_check_does_match = not isinstance(pattern, type) and callable(pattern) and pattern(arguments)
            if the_type_pattern_does_match or the_callable_pattern_check_does_match:
                data, kwargs = converter(data)
                break
        
        self._trigger("send", data, bypass_purification=kwargs.get("bypass_purification", False))

def register_large(data_format, data_id, data_as_bytes):
    ensure_server_is_running()
    base_url = _get_base_url()
    data_format = data_format.replace("/", r"%2F")
    return requests.post(
        f'{base_url}/large/set/{data_format}/{data_id}',
        files={
            'file': ("large_file", data_as_bytes),
            'Content-Type': data_format,
        },
    )

# kill the server on exit, unless the data has not been viewed yet
@atexit.register
def check_on_server():
    # if the data has been viewed, then stop the server (data will still be available in browser)
    if _contact_server("was_data_seen", catch_all_errors=True):
        _process and _process.kill()
    else:
        base_url = _get_base_url()
        print('')
        print(f'[silver_spectacle] There were unviewed results')
        print(f'[silver_spectacle] So the display server is still running at: {base_url}')
        print(f'[silver_spectacle] (use the stop server button to kill it now)')
        print('')