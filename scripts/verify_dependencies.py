import asyncio
import base64
import gzip
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer


async def verify_aiohttp():
    async def echo(request):
        return web.Response(body=await request.read())

    async def form(request):
        return web.json_response(dict(await request.post()))

    async def websocket(request):
        ws = web.WebSocketResponse(max_msg_size=64)
        await ws.prepare(request)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws.send_str(msg.data)
        return ws

    app = web.Application()
    app.add_routes([web.post('/echo', echo), web.post('/form', form), web.get('/ws', websocket)])
    async with TestClient(TestServer(app)) as client:
        async with client.post('/echo', data=gzip.compress(b'compressed payload'), headers={'Content-Encoding': 'gzip'}) as response:
            assert response.status == 200
            assert await response.read() == b'compressed payload'
        async with client.post('/form', data={'query': 'ACTG'}) as response:
            assert await response.json() == {'query': 'ACTG'}
        async with client.ws_connect('/ws', compress=15) as ws:
            await ws.send_str('echo')
            assert (await ws.receive(timeout=5)).data == 'echo'
            await ws.send_str('x' * 128)
            message = await ws.receive(timeout=5)
            assert message.type == aiohttp.WSMsgType.CLOSE, message
            assert message.data == 1009, message
    print(f'PASS aiohttp {aiohttp.__version__}: gzip HTTP, forms, compressed WebSocket, message-size rejection')


def verify_powerurl():
    os.environ['LINE_BOT_API_TOKEN'] = 'test-token'
    os.environ['LINE_BOT_CHANNEL_SECRET'] = 'test-secret'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import app

    client = app.app.test_client()
    assert client.get('/hello').status_code == 200
    assert client.get('/missing').status_code == 404
    app.url_mapping['sample'] = 'https://example.com/'
    response = client.get('/sample')
    assert response.status_code == 302
    assert response.headers['Location'] == 'https://example.com/'
    body = json.dumps({'destination': 'test', 'events': [{
        'type': 'message', 'message': {'id': '1', 'type': 'text', 'text': 'Shorten: https://example.com/'},
        'timestamp': 0, 'source': {'type': 'user', 'userId': 'test'}, 'replyToken': 'test', 'mode': 'active'
    }]})
    signature = base64.b64encode(hmac.new(b'test-secret', body.encode(), hashlib.sha256).digest()).decode()
    with patch.object(app.line_bot_api, 'reply_message') as reply:
        response = client.post('/callback', data=body, headers={'X-Line-Signature': signature}, content_type='application/json')
        assert response.status_code == 200, response.data
        reply.assert_called_once()
        assert 'Shortened URL:' in reply.call_args.args[1].text
    print('PASS powerUrl: hello, missing link, redirect, signed LINE webhook with mocked reply')


if __name__ == '__main__':
    asyncio.run(verify_aiohttp())
    if '--aiohttp-only' not in sys.argv:
        verify_powerurl()

