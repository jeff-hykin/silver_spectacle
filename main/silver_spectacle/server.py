from aiohttp import web
import socketio 
import sys
import argparse 
import math
import asyncio
from time import time as now


# 
# args setup
# 
parser = argparse.ArgumentParser(description="aiohttp server") 
parser.add_argument('--port') 
parser.add_argument('--custom-css', default="") 
parser.add_argument('--custom-js', default="")
args = parser.parse_args()

# globals 
last_time_data_was_viewed = -math.inf
last_time_data_was_updated = now()

# 
# server setup
# 
app = web.Application()
routes = web.RouteTableDef()
sio = socketio.AsyncServer(); sio.attach(app)
display_requests = "{}"

@routes.get('/')
async def index(request): 
    global display_requests
    from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath
    try:
        with open(join(dirname(__file__), "index.html"),'r') as f:
            output = f.read()
    except:
        output = None
    
    output = output.replace('''"""+display_requests+r"""''', display_requests)
    output = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <style>
                '''+args.custom_css+'''
            </style>
            <script>
                '''+args.custom_js+'''
            </script>
    '''+ output
    last_time_data_was_viewed = now()
    return web.Response(text=output, content_type='text/html')

@routes.get('/ping')
async def ping(request):
    return web.Response(text='"pong"')

@routes.get('/kill')
async def kill(request):
    await sio.emit('kill:response', '"imded"')
    exit()
    return web.Response(text='"imded"')

@routes.get('/was_viewed')
async def was_viewed(request):
    # if data was viewed more recently than it was updated
    if last_time_data_was_viewed >= last_time_data_was_updated:
        return web.Response(text="true")
    else:
        return web.Response(text="false")

@routes.get('/web_just_viewed')
async def web_just_viewed(request):
    last_time_data_was_viewed = now()

@routes.post('/update')
async def update(request):
    global display_requests
    display_requests = await request.text()
    last_time_data_was_updated = now()
    await sio.emit('update', display_requests)
    return web.Response(text="null")

# 
# start server
# 
app.add_routes(routes); web.run_app(app, port=args.port) 