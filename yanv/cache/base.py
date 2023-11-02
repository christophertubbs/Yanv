"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing
import random
import string

import pandas


_DATA_ID_LENGTH = 5
_DATA_ID_CHARACTER_SET = string.hexdigits


def generate_data_id() -> str:
    return ''.join(random.choices(population=_DATA_ID_CHARACTER_SET, k=_DATA_ID_LENGTH))


class FrameCache(typing.Protocol):
    @abc.abstractmethod
    def add(self, frame: pandas.DataFrame):
        ...

    @abc.abstractmethod
    def remove(self, data_id: str):
        ...

    @abc.abstractmethod
    def __len__(self) -> int:
        ...

    @abc.abstractmethod
    def keys(self) -> typing.Iterable[str]:
        ...

    @abc.abstractmethod
    def clean_up(self):
        ...

    @abc.abstractmethod
    def clear(self):
        ...

    @abc.abstractmethod
    def get(self, key: str, default: pandas.DataFrame = None) -> typing.Optional[pandas.DataFrame]:
        ...


CACHE_TYPE = typing.TypeVar("CACHE_TYPE", bound=FrameCache, covariant=True)