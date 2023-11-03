"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib
import typing

from aiohttp import web

from yanv.utilities.common import get_html_response

INDEX_PATH = (pathlib.Path(__file__).parent.parent / "static" / "templates" / "index.html").resolve()


async def handle_index(request: web.Request) -> web.Response:
    print("Got into the index view")
    return get_html_response(INDEX_PATH)
