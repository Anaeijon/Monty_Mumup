"""
Serve Mediaplayer Websocket Server.

MIT License
Copyright (c) 2017 David Döring (https://github.com/Anaeijon)
see LICENSE file.

This is a synchonous HTTP and Websocket Server to serve Mediaplayer Websocket
    and all needed file for Client Website to interact with Websocket.
VLC-Player is used as Mediaplayer.
Requiers Python 3.6.
"""
# TODO: check, why big title indexes in vlc cause errors
# TODO: avoid VLC-RC connection for now, allways use HTTP

import asyncio
import sys
import argparse
from aiohttp import web
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from vlc.vlc import VLC, MRL
from pprint import pprint
loop = asyncio.get_event_loop()


class AsyncHTTPWebSocketsHandler(web.View):
    """
    Asynchronous Handler for HTTP- and Websocket-Requests.

    Asynchonous implementation of Request handler which can serve HTTP-Files
        and a WebSocket on the same Port and Route.
    This is possible because every Websocket-Request starts as simple
        HTTP-GET-Request.
    The Client asks for "Upgrade" to 'websocket' in HTTP-Header.
    If the HTTP-Request asks for upgrade to 'websocket', this server will keep
        the task alive and initiate a WebSocketResponse until the WebSocket is
        closed by client.
    If the HTTP-Request doesn't ask for upgrade to 'websocket', the request is
        handled by a usual HTTP-GET-handler.
    """

    webclient_path = './webclient/'
    art_path = 'art/'

    async def on_ws_message(self, ws, msg):
        """Do on incoming websocket message."""
        data = msg.json()
        player = self.request.app['player']
        if 'command' in data:
            command = data['command']
            if command == 'play':
                if 'value' in data:
                    try:
                        player.play(int(data['value']))
                    except TypeError as err:
                        pprint(err)
                        pprint(id)
                else:
                    player.play()
                is_playing = player.is_playing()
                for wss in self.request.app['websockets']:
                    await ws.send_json({
                        'command': 'playing',
                        'value': is_playing
                    })
            elif command == 'pause':
                if 'id' in data:
                    player.pause(id)
                else:
                    player.pause()
                is_playing = player.is_playing()
                for wss in self.request.app['websockets']:
                    await ws.send_json({
                        'command': 'playing',
                        'value': is_playing
                    })
            elif command == 'stop':
                player.stop()
                is_playing = player.is_playing()
                for wss in self.request.app['websockets']:
                    await ws.send_json({
                        'command': 'playing',
                        'value': is_playing
                    })
            elif command == 'next':
                player.next()
                title = player.get_title()
                for wss in self.request.app['websockets']:
                    await ws.send_json({'command': 'title', 'value': title})
            elif command == 'previous':
                player.previous()
                title = player.get_title()
                for wss in self.request.app['websockets']:
                    await ws.send_json({'command': 'title', 'value': title})
            elif command == 'seek':
                if 'value' in data:
                    player.seek(data['value'])
                    time = player.get_time()
                    position = player.get_position()
                    for wss in self.request.app['websockets']:
                        await ws.send_json({'command': 'time', 'value': time})
                        await ws.send_json({
                            'command': 'position',
                            'value': position
                        })
            elif command == 'volup':
                if 'value' in data:
                    player.volup(data['value'])
                    volume = player.get_volume()
                    for wss in self.request.app['websockets']:
                        await ws.send_json({
                            'command': 'volume',
                            'value': volume
                        })
            elif command == 'voldown':
                if 'value' in data:
                    player.voldown(data['value'])
                    volume = player.get_volume()
                    for wss in self.request.app['websockets']:
                        await ws.send_json({
                            'command': 'volume',
                            'value': volume
                        })
            elif command == 'volume':
                if 'value' in data:
                    player.set_volume(data['value'])
                    volume = player.get_volume()
                    for wss in self.request.app['websockets']:
                        await ws.send_json({
                            'command': 'volume',
                            'value': volume
                        })
            elif command == 'repeat':
                if 'value' in data:
                    player.repeat(data['value'])
                else:
                    player.repeat()
                repeat = player.get_repeat()
                loop = player.get_loop()
                for wss in self.request.app['websockets']:
                    await ws.send_json({'command': 'repeat', 'value': repeat})
                    await ws.send_json({'command': 'loop', 'value': loop})
            elif command == 'loop':
                if 'value' in data:
                    player.loop(data['value'])
                else:
                    player.loop()
                repeat = player.get_repeat()
                loop = player.get_loop()
                for wss in self.request.app['websockets']:
                    await ws.send_json({'command': 'repeat', 'value': repeat})
                    await ws.send_json({'command': 'loop', 'value': loop})
            elif command == 'random':
                if 'value' in data:
                    player.random(data['value'])
                else:
                    player.random()
                random = player.get_random()
                for wss in self.request.app['websockets']:
                    await ws.send_json({'command': 'random', 'value': random})
            elif command == 'is_playing':
                await ws.send_json({
                    'command': 'playing',
                    'value': player.is_playing()
                })
            elif command == 'get_playlist':
                await ws.send_json({
                    'command': 'playlist',
                    'value': player.get_playlist()
                })
            elif command == 'get_title':
                await ws.send_json({
                    'command': 'title',
                    'value': player.get_title()
                })
            elif command == 'get_position':
                """Position in Stream between 0 .. 1"""
                await ws.send_json({
                    'command': 'position',
                    'value': player.get_position()
                })
            elif command == 'get_time':
                """Get seconds elapsed since stream's beginning"""
                await ws.send_json({
                    'command': 'time',
                    'value': player.get_time()
                })
            elif command == 'get_repeat':
                await ws.send_json({
                    'command': 'repeat',
                    'value': player.get_repeat()
                })
            elif command == 'get_volume':
                await ws.send_json({
                    'command': 'volume',
                    'value': player.get_volume()
                })
            elif command == 'get_length':
                await ws.send_json({
                    'command': 'length',
                    'value': player.get_length()
                })
            elif command == 'get_loop':
                await ws.send_json({
                    'command': 'loop',
                    'value': player.get_loop()
                })
            elif command == 'get_repeat':
                await ws.send_json({
                    'command': 'repeat',
                    'value': player.get_repeat()
                })
            elif command == 'get_random':
                await ws.send_json({
                    'command': 'random',
                    'value': player.get_random()
                })

    async def on_ws_connected(self, ws):
        """Do after establishing websocket connection."""
        self.request.app['websockets'].append(ws)

    async def on_ws_closed(self, ws):
        """Do after closing websocket."""
        self.request.app['websockets'].remove(ws)

    async def get(self):
        """Decide if websocket or common http-get request."""
        if self.request.headers.get('Upgrade', None) == 'websocket':
            return await self._handle_websocket()
        else:
            return await self._handle_http()

    async def _handle_websocket(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        await self.on_ws_connected(ws)
        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.tp == web.MsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await self.on_ws_message(ws, msg)
            elif msg.tp == web.MsgType.error:
                print('ws exception %s, closed' % ws.exception())

        await self.on_ws_closed(ws)
        return ws

    async def _handle_http(self):
        path = self.request.match_info['path']
        pprint(path)
        if path == '':
            p = Path(self.webclient_path + "index.html")
            return web.FileResponse(path=p)
        # if art is requested, search and return cover image:
        elif path.startswith(self.art_path):
            player = self.request.app['player']
            picture_path = self.request.app['picture_path']
            full_title = player.get_title()
            title_path = unquote('/'.join(full_title['uri'].split('/')[2:-1]))
            mrl_type = unquote(full_title['uri'].split('/')[0])
            title = unquote(full_title['uri'].split('/')[-1])
            fname = '.'.join(title.split('.')[0:-1])
            album = fname.split('(')[-1].split(')')[0]
            if mrl_type.startswith('file'):
                path = Path(title_path + '/' + fname + ".jpg")
                if path.is_file():
                    return web.FileResponse(path=path)
                path = Path(title_path + '/' + fname + ".png")
                if path.is_file():
                    return web.FileResponse(path=path)
                path = Path(title_path + '/' + album + ".jpg")
                if path.is_file():
                    return web.FileResponse(path=path)
                path = Path(title_path + '/' + album + ".png")
                if path.is_file():
                    return web.FileResponse(path=path)
                path = Path(title_path + '/' + "album.jpg")
                if path.is_file():
                    return web.FileResponse(path=path)
                path = Path(title_path + '/' + "album.png")
                if path.is_file():
                    return web.FileResponse(path=path)
            path = Path(picture_path + '/' + fname + ".jpg")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + fname + ".png")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + album + ".jpg")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + album + ".png")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + "album.jpg")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + "album.png")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + "default.jpg")
            if path.is_file():
                return web.FileResponse(path=path)
            path = Path(picture_path + '/' + "default.png")
            if path.is_file():
                return web.FileResponse(path=path)
            else:
                return web.Response(text="No art found.")

        else:
            # TODO: sanitize requested path
            p = Path(self.webclient_path + path)
            if p.is_file():
                return web.FileResponse(path=p)
            else:
                return web.Response(status=404, text="404: File not Found.")


async def listen_to_playlist(player, app, sleep_time=1, recache_time=10):
    """Look for changes in playlist and send them to all websockets."""
    playlist = None
    last_cached_timestamp = datetime.now()
    while True:
        await asyncio.sleep(sleep_time)
        now = datetime.now()
        if (now - last_cached_timestamp).total_seconds() > recache_time:
            player.get_playlist()
        new_playlist = player.get_cached_playlist()
        if new_playlist is not playlist:
            last_cached_timestamp = now
            playlist = new_playlist
            for ws in app['websockets']:
                await ws.send_json({'command': 'playlist', 'value': playlist})


async def listen_to_function(app,
                             function,
                             function_name=None,
                             sleep_time=0.5,
                             recache_time=30):
    """
    Listen to changes and send to websockets.

    Listen to changes at the return of <function> in interval of <sleep_time>.
    Send changes to all websocket clients.
    """
    last_state = None
    if function_name is None:
        function_name = function.__name__
    last_cached_timestamp = datetime.now()
    while True:
        await asyncio.sleep(sleep_time)
        now = datetime.now()
        new_state = function()
        if last_state != new_state or (
                now - last_cached_timestamp).total_seconds() > recache_time:
            last_cached_timestamp = now
            last_state = function()
            for ws in app['websockets']:
                await ws.send_json({
                    'command': function_name,
                    'value': last_state
                })


parser = argparse.ArgumentParser(
    description='Monty Mumup - A Python based MultiUserMUsicPlayer.')
parser.add_argument('music_directory', help='directory where music is stored')
parser.add_argument(
    '--port',
    dest='port',
    default=8000,
    type=int,
    help='port where this will be served')
parser.add_argument(
    '--vlc-port',
    dest='vlc_port',
    default=8080,
    type=int,
    help='port where vlc http backend will be running')

args = parser.parse_args()
if args.vlc_port == args.port:
    pprint("use another port or set --vlc-port")
    sys.exit()

vlc = VLC(interfaces=(['http']), http_port=args.vlc_port)
vlc.stop()
vlc.clear()
vlc.add(MRL(MRL.DIR, args.music_directory))
app = web.Application(loop=loop)
app['websockets'] = []
app['player'] = vlc
app['picture_path'] = args.music_directory
# catch all routes and requests with Handler:
app.router.add_route('*', '/{path:.*}', AsyncHTTPWebSocketsHandler)
# dictionary of listeners aviable for websocket broadcasting
listener_tasks = {
    'position': (vlc.get_position, 0.1),
    'time': (vlc.get_time, 0.1),
    'playing': (vlc.is_playing, 0.1),
    'title': (vlc.get_title, 0.5),
    'repeat': (vlc.get_repeat, 0.5),
    'loop': (vlc.get_loop, 0.5),
    'random': (vlc.get_random, 0.5),
    'volume': (vlc.get_volume, 0.5),
}
# start all the listeners
for name in listener_tasks:
    loop.create_task(
        listen_to_function(
            app=app,
            function=listener_tasks[name][0],
            function_name=name,
            sleep_time=listener_tasks[name][1]))
# listening to playlist is optimized, start task seperately
loop.create_task(listen_to_playlist(vlc, app))
web.run_app(app, port=args.port)
