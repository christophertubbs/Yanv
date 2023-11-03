"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import os
import pathlib
import typing

from aiohttp import web

from yanv.handlers import handle_index
from yanv.handlers import register_resource_handlers
from yanv.handlers import socket_handler

DEFAULT_PORT = 10324


def main(port: int, *argv) -> typing.NoReturn:
    application = web.Application()

    register_resource_handlers(application)

    application.add_routes([
        web.get("/get", handler=handle_index),
        web.get("/ws", handler=socket_handler)
    ])

    web.run_app(application, port=port)


if __name__ == "__main__":
    main(port=DEFAULT_PORT)