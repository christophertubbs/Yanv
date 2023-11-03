"""
@TODO: Put a module wide description here
"""
from __future__ import annotations
import typing
import pathlib
from dataclasses import dataclass

from aiohttp import web

RESOURCE_DIRECTORY = pathlib.Path(__file__).parent.parent / "static"
SCRIPT_DIRECTORY = RESOURCE_DIRECTORY / "scripts"


@dataclass
class RouteInfo:
    path: str
    handler: typing.Callable[[web.Request], typing.Coroutine[typing.Any, typing.Any, web.Response]]
    name: typing.Optional[str]

    def register_get(self, application: web.Application):
        application.add_routes([
            web.get(self.path, handler=self.handler)
        ])


async def get_script(request: web.Request) -> web.Response:
    script_name = request.match_info['name']

    script_path = SCRIPT_DIRECTORY / script_name

    if script_path.exists():
        with open(script_path) as script_file:
            return web.Response(
                text=script_file.read(),
                content_type="application/javascript"
            )

    return web.HTTPNotFound(text=f"No script was found at '{script_path}'")

RESOURCE_ROUTES = [
    RouteInfo(path="/scripts/{name}", handler=get_script, name="get_script")
]


def register_resource_handlers(application: web.Application):
    for route in RESOURCE_ROUTES:
        route.register_get(application=application)