"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing
from os import PathLike

import pandas

from yanv.cache import CACHE_TYPE
from yanv.cache import InMemoryFrameCache


class BaseBackend(typing.Protocol):
    @classmethod
    def get_default_cache(cls) -> CACHE_TYPE:
        return InMemoryFrameCache()

    @property
    @abc.abstractmethod
    def cache(self) -> CACHE_TYPE:
        ...

    @abc.abstractmethod
    def load(self, path: PathLike, *args, **kwargs) -> str:
        ...