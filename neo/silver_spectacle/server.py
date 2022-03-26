# encoding: utf-8
from aiohttp import web
import socketio 
import sys
import argparse 
import math
import asyncio
from time import time as now
import sys
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath
__dir__ = dirname(__file__)


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
debugging = False

# 
# server setup
# 
app = web.Application(client_max_size=(1024 ** 2 * 100))
routes = web.RouteTableDef()
options = {} if not debugging else dict(logger=True, engineio_logger=True)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*", **options); sio.attach(app)
cards = "{}"
large_data = {}

if debugging: print('starting server') 

app.router.add_static('/files', __dir__+"/files")

@routes.post('/ping')
async def ping(request : web.Request):
    return web.Response(text='"pong"')

@routes.post('/stop')
async def stop(request : web.Request):
    await sio.emit('stop:response', '"imded"')
    exit()
    return web.Response(text='"imded"')

@routes.post('/was_data_seen')
async def was_data_seen(request : web.Request):
    # if data was viewed more recently than it was updated
    if last_time_data_was_viewed >= last_time_data_was_updated:
        return web.Response(text="true")
    else:
        return web.Response(text="false")

@routes.post('/web_received_data')
async def web_received_data(request : web.Request):
    global last_time_data_was_viewed
    last_time_data_was_viewed = now()
    return web.Response(text="true")

@routes.post('/new_card')
async def new_card(request : web.Request):
    global cards
    global last_time_data_was_updated
    try:
        cards = await request.text()
    except Exception as error:
        print('error = ', error)
    print('backend: awaited request.text')
    last_time_data_was_updated = now()
    print('backend: emitting new_card')
    await sio.emit('new_card', cards)
    print('backend: emitted new_card')
    return web.Response(text="null")

@routes.post('/card_trigger')
async def card_trigger(request : web.Request):
    global cards
    global last_time_data_was_updated
    data = await request.text()
    last_time_data_was_updated = now()
    await sio.emit('card_trigger', data)
    return web.Response(text="null")

@routes.post('/large/set/{content_type}/{data_id}')
async def set_large_data(request : web.Request):
    global large_data
    content_type = request.match_info["content_type"]
    content_type = content_type.replace(r"%2F", "/")
    large_data_id = request.match_info["data_id"]
    # save in ram
    post_result = await request.post()
    large_file = post_result.get("file")
    if large_file is not None:
        large_data[large_data_id] = large_file.file.read()
    return web.Response(text="null")

@routes.get('/large/get/{content_type}/{data_id}')
async def get_large_data(request : web.Request):
    global large_data
    content_type = request.match_info["content_type"]
    content_type = content_type.replace(r"%2F", "/")
    large_data_id = request.match_info["data_id"]
    return web.Response(
        content_type=content_type,
        body=large_data[large_data_id],
    )

# 
# start server
# 
app.add_routes(routes); web.run_app(app, port=args.port) 