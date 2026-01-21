"""
@TODO: Put a module wide description here
"""
import sys
import typing
import logging
import pathlib
import collections.abc as generic
import os

from aiohttp import web
from aiohttp.abc import AbstractView
from aiohttp.abc import Request
from aiohttp.abc import StreamResponse
from aiohttp.web_routedef import RouteDef

from yanv.application_details import ALLOW_REMOTE
from yanv.application_details import INDEX_PAGE
from yanv.handlers import navigate
from yanv.launch_parameters import ApplicationArguments
from yanv.utilities import common
from yanv.handlers import handle_index
from yanv.handlers import register_resource_handlers
from yanv.handlers import socket_handler

from yanv.application_details import APPLICATION_NAME
from yanv.application_details import DEBUG_MODE

RequestHandler = typing.Type[AbstractView] | generic.Callable[[Request], generic.Awaitable[StreamResponse]]

# Name won't be '__main__' if a registered script from pip is called, so check endswith to ensure it is called correctly
if __name__.endswith("__main__"):
    logging.basicConfig(
        level=logging.DEBUG if DEBUG_MODE else logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s %(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
        force=True,
    )

    loggers_to_quiet: list[str] = [
        "aiohttp",
        "asyncio",
        "aiohttp.access",
        "urllib3.connectionpool",
        "h5py._conv"
    ]

    for logger_name in loggers_to_quiet:
        logger: logging.Logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


LOGGER: logging.Logger = logging.getLogger(pathlib.Path(__file__).stem)


def add_routes(application: web.Application, routes: generic.Iterable[RouteDef]) -> None:
    """
    Ensure that given routes may be added and attach them to the web application

    Args:
        application: The web application that will be interpretting requests
        routes: The routes that the web application will handle
    """
    if not ALLOW_REMOTE:
        invalid_routes: list[str] = list()
        for route in routes:
            handler: RequestHandler = route.handler

            if not getattr(handler, common.LOCAL_ONLY_IDENTIFIER, False):
                invalid_routes.append(route.path)

        if invalid_routes:
            message = (
                f"Cannot register routes - "
                f"the following routes were not marked as local only: {', '.join(invalid_routes)}"
            )
            raise ValueError(message)

    application.add_routes(routes)


def get_routes() -> generic.Iterable[RouteDef]:
    """
    Get the collection of routes to handle
    """
    return [
        web.get(f"/{INDEX_PAGE}", handler=handle_index),
        web.get("/navigate", handler=navigate),
        web.get("/ws", handler=socket_handler),
    ]


def serve(arguments: ApplicationArguments | tuple | None = None) -> int:
    """
    The primary entry point for the server

    Args:
        arguments: Arguments that may override basic parameters of the server, such as what port to connect to

    Returns:
        The exit code for the application
    """
    if isinstance(arguments, tuple):
        arguments: ApplicationArguments = ApplicationArguments(*arguments)
    elif arguments is None:
        arguments: ApplicationArguments = ApplicationArguments()

    try:
        application: web.Application = web.Application()
    except KeyboardInterrupt:
        LOGGER.info(f"Keyboard interrupt encountered when creating the web application. Now exiting...")
        return 0
    except BaseException as e:
        LOGGER.critical(f"Could not create the base application: {e}", exc_info=True)
        return 1

    try:
        register_resource_handlers(application)
    except KeyboardInterrupt:
        LOGGER.info(f"Keyboard interrupt encountered when registering static resources. Now exiting...")
        return 0
    except BaseException as e:
        LOGGER.critical(f"Could not register the location of static resources: {e}", exc_info=True)
        return 1

    try:
        routes: generic.Iterable[RouteDef] = get_routes()
        add_routes(application=application, routes=routes)
    except KeyboardInterrupt:
        LOGGER.info(f"Keyboard interrupt encountered when registerring routes. Now exiting...")
        return 0
    except BaseException as e:
        LOGGER.critical(f"Could not set up routing: {e}", exc_info=True)
        return 1

    LOGGER.info(f"Access {APPLICATION_NAME} from http://0.0.0.0:{arguments.port}/{INDEX_PAGE}")

    try:
        web.run_app(application, port=arguments.port)
    except KeyboardInterrupt:
        LOGGER.info(f"Keyboard interrupt encountered while running the server. Now exiting...")
        pass
    except BaseException as e:
        LOGGER.critical(f"An error occurred when binding and running the server: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code: int = serve(ApplicationArguments(*sys.argv[1:]))
    except KeyboardInterrupt:
        LOGGER.critical(f"Uncaught keyboard interrupt encountered. Exitting...")
        exit_code: int = 0
    except BaseException as unexpected_error:
        LOGGER.critical(f"Unexpected error encountered: {unexpected_error}", exc_info=True)
        exit_code: int = 1

    sys.exit(exit_code)
