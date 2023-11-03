"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import os
import typing
import inspect

from aiohttp import web


_CLASS_TYPE = typing.TypeVar("_CLASS_TYPE")


def get_subclasses(base: typing.Type[_CLASS_TYPE]) -> typing.List[typing.Type[_CLASS_TYPE]]:
    """
    Gets a collection of all concrete subclasses of the given class in memory

    A subclass that has not been imported will not be returned

    Example:
        >>> import numpy
        >>> get_subclasses(float)
        [numpy.float64]

    Args:
        base: The base class to get subclasses from

    Returns:
        All implemented subclasses of a specified types
    """
    concrete_classes = [
        subclass
        for subclass in base.__subclasses__()
        if not inspect.isabstract(subclass)
    ]

    for subclass in base.__subclasses__():
        concrete_classes.extend([
            cls
            for cls in get_subclasses(subclass)
            if cls not in concrete_classes
               and not inspect.isabstract(cls)
        ])

    return concrete_classes


def get_html_response(html_file: os.PathLike, context: typing.Dict[str, typing.Any] = None) -> web.Response:
    with open(html_file) as html_data:
        return web.Response(text=html_data.read(), content_type="text/html")