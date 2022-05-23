import os
import requests
import subprocess
import time
import sys
import atexit
from super_hash import super_hash

from blissful_basics import print, flatten, to_pure, stringify, stats, product, countdown, is_generator_like, now, large_pickle_save, large_pickle_load, FS, Object

__dirname__ = os.path.dirname(__file__)
debugging = False

#
# 
# main code
# 
#
class ServerApi:
    server_file_path = os.path.join(__dirname__, "server.py")
    
    def __init__(self, port=9900, connection_timeout=10, base_url=None):
        self.port = port
        self.connection_timeout = connection_timeout
        self.process = None
        self._base_url = base_url
    
    @property
    def base_url(self):
        if self._base_url:
            return self._base_url
        else:
            return f"http://localhost:{self.port}"
        
    def contact_server(self, endpoint, data=None, catch_all_errors=False, ensure_server_is_up=True, bypass_purification=False):
        import json
        try:
            # remove complex classes in favor of simple lists/dicts (NOTE: doesn't remove recursive values)
            if not bypass_purification:
                data = _to_pure(data)
            if ensure_server_is_up:
                ensure_is_running()
            base_url = self.base_url
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

    def ensure_is_running(self):
        result = self.contact_server("ping", catch_all_errors=True, ensure_server_is_up=False)
        # if no pong, then start the server and wait
        if result != "pong":
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    self.server_file_path,
                    "--port", str(self.port),
                ],
                **(dict(stdout=sys.stdout) if debugging else dict(stdout=subprocess.PIPE)),
                # stderr=subprocess.STDOUT,
            )
            start = now()
            while result != "pong":
                if now() - start > self.connection_timeout:
                    print(f"\n",  file=sys.stderr)
                    print(f"[silver_spectacle] Tried to start a server on port {self.port}",  file=sys.stderr)
                    print(f"[silver_spectacle] however after waiting {self.connection_timeout} seconds (Server.connection_timeout)",  file=sys.stderr)
                    print(f"[silver_spectacle] the server failed to respond to ping requests",  file=sys.stderr)
                    print(f"[silver_spectacle] no error will be thrown, but output likely will not be displayed",  file=sys.stderr)
                    print(f"[silver_spectacle] {self.process}",  file=sys.stderr)
                    print(f"\n",  file=sys.stderr)
                    break
                result = self.contact_server("ping", catch_all_errors=True, ensure_server_is_up=False)
            # if started successfully
            if result == "pong":
                address = self.base_url
                print(f"[silver_spectacle] server started at: {address}")
                
            return False
        else:
            return True
    
    def spectacle_init(self, *, class_id, instance_id, value):
        self.contact_server(endpoint="runtime/spectacle_init", data=dict(class_id=class_id, instance_id=instance_id, value=value))
    
    def spectacle_update(self, *, class_id, instance_id, value, path, action, args, time):
        self.contact_server(endpoint="runtime/spectacle_update", data=dict(class_id=class_id, instance_id=instance_id, path=path, action=action, args=args, time=time))
    
    def register_large(self, content_type, data_as_bytes):
        self.ensure_is_running()
        data_id = super_hash((content_type, data_as_bytes))
        content_type = content_type.replace("/", r"%2F")
        return requests.post(
            f'{self.base_url}/runtime/large/set/{content_type}/{data_id}',
            files={
                'file': ("large_file", data_as_bytes),
                'Content-Type': content_type,
            },
        )


server_api = ServerApi()