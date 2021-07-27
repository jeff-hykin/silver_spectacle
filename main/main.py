import os
import requests
import subprocess
import time
import sys

_settings = {
    "port": 9900,
    "server_start_timeout": 10,
}
def configure(settings):
    global _settings
    _settings = {
        **_settings,
        **settings,
    }

def ensure_server_is_running():
    global _settings
    port = _settings["port"]
    server_start_timeout = _settings["server_start_timeout"]
    result = None
    try:
        result = requests.get(f'http://localhost:{_settings["port"]}/ping')
    except Exception as error:
        pass
    # if no pong, then start the server and wait
    if not result or result.text != "pong":
        process = subprocess.Popen(
            ["python", os.path.join(os.path.dirname(__file__), "server.py"), "--port", str(_settings["port"])],
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDERR
        )
        start = time.time()
        while not result or result.text != "pong":
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
        return False
    else:
        return True

def display(data, component):
    global _settings
    port = _settings["port"]
    # if server wasnt already running
    server_was_running = ensure_server_is_running()
    print('server_was_running = ', server_was_running)
    # send data and method to 
    response = requests.post(
        f'http://localhost:{port}/post',
        json={
            "data": data,
            "component": component,
        },
    )
    print('response = ', response.text)