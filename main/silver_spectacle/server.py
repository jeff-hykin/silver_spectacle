from aiohttp import web
import socketio 
import sys
import argparse 


# 
# args setup
# 
parser = argparse.ArgumentParser(description="aiohttp server") 
parser.add_argument('--port') 
args = parser.parse_args()

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
    return web.Response(text=output, content_type='text/html')

@routes.get('/ping')
async def ping(request):
    return web.Response(text="pong")

@routes.post('/update')
async def update(request):
    global display_requests
    display_requests = await request.text()
    await sio.emit('update', display_requests)
    return web.Response(text="null")

# 
# start server
# 
app.add_routes(routes); web.run_app(app, port=args.port) 