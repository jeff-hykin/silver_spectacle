# encoding: utf-8
from blissful_basics import print, flatten, to_pure, stringify, stats, product, countdown, is_generator_like, now, large_pickle_save, large_pickle_load, FS, Object
from aiohttp import web
import socketio 
import sys
import argparse 
import math
import asyncio
from random import random, sample, choices
from time import time as now
import sys
import json
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath

__dir__ = dirname(__file__)


# 
# args setup
# 
with print.indent:
    parser = argparse.ArgumentParser(description="aiohttp server") 
    parser.add_argument('--port') 
    args = parser.parse_args()

# globals 
with print.indent:
    debugging = False
    self = Object(
        last_time_data_was_viewed = -math.inf,
        last_time_data_was_updated = now(),
        spectacle_instances = {},
        large_data = {},
        large_data_content_type = {},
    )

# 
# server obj setup
# 
if debugging: print('starting server')
with print.indent:
    app        = web.Application(client_max_size=(1024 ** 2 * 100))
    routes     = web.RouteTableDef()
    options    = {} if not debugging else dict(logger=True, engineio_logger=True)
    sio        = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*", **options); sio.attach(app)
    async def schedule_shutdown():
        # allow time to respond to request
        await asyncio.sleep(200)
        if debugging: print("Start shutting down")
        await app.shutdown()
        if debugging: print("Start cleaning up")
        await app.cleanup()
        # force quit
        exit()
    
# 
# tools
# 
with print.indent:
    def run_with(*args, **kwargs):
        def decorator(function_being_wrapped):
            # run immediately
            function_being_wrapped(*args, **kwargs)
            return function_being_wrapped
        return decorator
    def json_post(*args, **kwargs):
        @routes.post(*args, **kwargs)
        async def wrapper(request : web.Request):
            args = await request.json()
            if isinstance(args, (list, tuple)):
                output = await function_being_wrapped(*args)
            elif isinstance(args, dict):
                output = await function_being_wrapped(**args)
            else:
                output = await function_being_wrapped(args)
            output = to_pure(output)
            return web.json_response(output)
        return wrapper
# 
# 
# Routes
# 
# 
app.router.add_static('/files', __dir__+"/files")

@json_post('/ping')
async def ping():
    return "pong"

@json_post('/frontend/stop')
async def stop():
    await sio.emit('server:status', '"stopping"')
    schedule_shutdown()
    return "stopping"

@json_post('/frontend/web_received_data')
async def web_received_data():
    self.last_time_data_was_viewed = now()
    return True

@json_post('/runtime/was_data_seen')
async def was_data_seen():
    # if data was viewed more recently than it was updated
    if self.last_time_data_was_viewed >= self.last_time_data_was_updated:
        return True
    else:
        return False

@json_post('/runtime/spectacle_init')
async def spectacle_init(*, class_id, instance_id, value):
    self.spectacle_instances[f"{class_id}:{instance_id}"] = value
    self.last_time_data_was_updated = now()

@json_post('/runtime/spectacle_update')
async def spectacle_update(*, class_id, instance_id, path, action, args):
    await sio.emit(
        f'spectacle:update:{class_id}:{instance_id}',
        json.dumps(dict(
            path=path,
            action=action,
            args=args
        ))
    )

@routes.post('/runtime/large/set/{content_type}/{data_id}')
async def set_large_data(request : web.Request):
    large_data_id = request.match_info["data_id"]
    # save the content_type
    self.large_data_content_type[large_data_id] = request.match_info["content_type"].replace(r"%2F", "/")
    # save in ram
    post_result = await request.post()
    large_file = post_result.get("file")
    if large_file is not None:
        self.large_data[large_data_id] = large_file.file.read()
    return web.Response(text="null")

@routes.get('/frontend/large/get/{data_id}')
async def get_large_data(request : web.Request):
    large_data_id = request.match_info["data_id"]
    return web.Response(
        content_type=self.large_data_content_type[large_data_id],
        body=self.large_data[large_data_id],
    )

# 
# start server
# 
app.add_routes(routes); web.run_app(app, port=args.port) 