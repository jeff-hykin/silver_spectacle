from silver_spectacle.runtime import Spectacle
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath

try:
    with open(dirname(__file__)+"/quick_line.html",'r') as f:
        html_string = f.read()
except:
    html_string = None

class QuickLine(Card):
    def _repr_html_(self):
        return html_string