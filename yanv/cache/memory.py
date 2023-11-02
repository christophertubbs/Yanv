"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import logging

from collections import Counter
from datetime import datetime

import pandas

from yanv.cache.base import FrameCache
from yanv.cache.base import generate_data_id

_DEFAULT_FRAME_LIMIT = 4


class InMemoryFrameCache(FrameCache):
    def __init__(self, limit: int = None):
        if limit is None or limit <= 0:
            limit = _DEFAULT_FRAME_LIMIT

        self._limit = limit
        self._frames: typing.Dict[str, pandas.DataFrame] = dict()
        self._last_access_times: Counter[str] = Counter()

    def add(self, frame: pandas.DataFrame) -> str:
        new_id = generate_data_id()
        self._frames[new_id] = frame
        self.touch_frame(new_id)

        self.clean_up()

        return new_id

    def get_id(self, frame: pandas.DataFrame) -> typing.Optional[str]:
        for data_id, cached_frame in self._frames.items():
            if frame == cached_frame:
                return data_id
        return None

    def touch_frame(self, data_id: str) -> int:
        new_timestamp = int(datetime.now().timestamp())
        self._last_access_times[data_id] = new_timestamp
        return new_timestamp

    def remove(self, data_id: str):
        if data_id in self._frames.keys():
            del self._frames[data_id]

        if data_id in self._last_access_times:
            del self._last_access_times[data_id]

    def __len__(self) -> int:
        return len(self._frames)

    def keys(self) -> typing.Iterable[str]:
        return self._frames.keys()

    def clean_up(self):
        while len(self._frames) > self._limit:
            least_recent_id, timestamp = self._last_access_times.most_common()[-1]
            logging.debug(f"Too many data frames detected - removing {least_recent_id}")
            self.remove(least_recent_id)

    def clear(self):
        self._frames = dict()
        self._last_access_times = Counter()

    def get(self, key: str, default: pandas.DataFrame = None) -> typing.Optional[pandas.DataFrame]:
        if key not in self._frames.keys():
            return default

        self.touch_frame(key)
        return self._frames[key]