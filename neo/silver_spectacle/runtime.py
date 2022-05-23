import os
import requests
import subprocess
import time
import sys
import atexit
from runtime_setup import server_api

from blissful_basics import print, flatten, to_pure, stringify, stats, product, countdown, is_generator_like, now, large_pickle_save, large_pickle_load, FS, Object

__dirname__ = os.path.dirname(__file__)
debugging = False

# kill the server on exit, unless the data has not been viewed yet
@atexit.register
def check_on_server():
    pass