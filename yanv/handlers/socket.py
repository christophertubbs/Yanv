"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import random
import string

from aiohttp import web
from aiohttp.abc import AbstractStreamWriter

from yanv.backend.base import BaseBackend
from yanv.backend.file import FileBackend

CONNECTION_ID_LENGTH = 5
CONNECTION_ID_CHARACTER_SET = string.hexdigits


async def socket_handler(request: web.Request) -> web.WebSocketResponse:
    socket_response = web.WebSocketResponse()

    connection_id = ''.join(random.choices(population=CONNECTION_ID_CHARACTER_SET, k=CONNECTION_ID_LENGTH))

    writer: AbstractStreamWriter = await socket_response.prepare(request=request)
    backend: BaseBackend = FileBackend()

    print(f"Connected to socket {connection_id} from {request.host}")

    for message in socket_response:
        pass

    print(f"Connection to Socket {connection_id} closing")

    return socket_response