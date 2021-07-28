import os
import requests
import subprocess
import time
import sys
import atexit

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
                "python",
                os.path.join(os.path.dirname(__file__), "server.py"),
                "--port", str(_settings["port"]),
                "--custom-css", _settings["custom_css"],
                "--custom-js", _settings["custom_js"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        start = time.time()
        while not result or result.text != '"pong"':
            if time.time() - start > _settings["server_start_timeout"]:
                print(f"\n",  file=sys.stderr)
                print(f"[silver_spectacle] Tried to start a server on port {port}",  file=sys.stderr)
                print(f"[silver_spectacle] however after waiting {server_start_timeout} seconds ('server_start_timeout')",  file=sys.stderr)
                print(f"[silver_spectacle] the server failed to respond to ping requests",  file=sys.stderr)
                print(f"[silver_spectacle] no error will be thrown, but output likely will not be displayed",  file=sys.stderr)
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
        