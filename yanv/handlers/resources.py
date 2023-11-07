"""
@TODO: Put a module wide description here
"""
from __future__ import annotations
import typing
import pathlib
from dataclasses import dataclass

from aiohttp import web

from yanv.utilities import mimetypes

RESOURCE_DIRECTORY = pathlib.Path(__file__).parent.parent / "static"
SCRIPT_DIRECTORY = RESOURCE_DIRECTORY / "scripts"
STYLE_DIRECTORY = RESOURCE_DIRECTORY / "style"

RESOURCE_MAP = {
    "scripts": SCRIPT_DIRECTORY,
    "script": SCRIPT_DIRECTORY,
    "style": STYLE_DIRECTORY,
    "styles": STYLE_DIRECTORY,
}


@dataclass
class RouteInfo:
    path: str
    handler: typing.Callable[[web.Request], typing.Coroutine[typing.Any, typing.Any, web.Response]]
    name: typing.Optional[str]

    def register_get(self, application: web.Application):
        application.add_routes([
            web.get(self.path, handler=self.handler)
        ])


def get_content_type(resource_type: str, filename: pathlib.Path) -> typing.Optional[str]:
    return mimetypes.get(filename.suffix)


def get_resource_directory(resource_type: str) -> pathlib.Path:
    return RESOURCE_MAP[resource_type]


async def get_resource(request: web.Request) -> web.Response:
    resource_type: str = request.match_info['resource_type']

    if resource_type not in RESOURCE_MAP:
        return web.HTTPNotAcceptable(text=f"{resource_type} is not a valid type of resource")

    resource_name: str = request.match_info['name']
    resource_directory = get_resource_directory(resource_type)
    resource_path = resource_directory / resource_name

    if resource_path.exists():
        content_type = get_content_type(resource_type, resource_path)

        if content_type.startswith("image") or content_type.startswith("video"):
            return web.Response(
                body=resource_path.read_bytes(),
                content_type=content_type
            )
        else:
            return web.Response(
                text=resource_path.read_text(),
                content_type=content_type
            )

    return web.HTTPNotFound(text=f"No resource was found at '{resource_path}'")

RESOURCE_ROUTES = [
    RouteInfo(path="/{resource_type}/{name:.*}", handler=get_resource, name="get_resource"),
]


def register_resource_handlers(application: web.Application):
    for route in RESOURCE_ROUTES:
        route.register_get(application=application)