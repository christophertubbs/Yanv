"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
import logging

from collections import Counter
from datetime import datetime

import pandas
import xarray

from yanv.cache.base import DatasetCache
from yanv.model.dataset import Dataset

_DEFAULT_FRAME_LIMIT = 4


class InMemoryFrameCache(DatasetCache):
    """
    XArray dataset cache that keeps data in memory
    """

    def __init__(self, limit: int = None):
        if limit is None or limit <= 0:
            limit = _DEFAULT_FRAME_LIMIT

        self._limit = limit
        self._datasets: typing.Dict[str, xarray.Dataset] = dict()
        self._last_access_times: Counter[str] = Counter()

    def add(self, data: xarray.Dataset) -> str:
        new_id: str = self._generate_data_id()
        self._datasets[new_id] = data
        self.touch_frame(new_id)

        self.clean_up()

        return new_id

    def get_id(self, frame: pandas.DataFrame) -> typing.Optional[str]:
        for data_id, cached_frame in self._datasets.items():
            if frame == cached_frame:
                return data_id
        return None

    def touch_frame(self, data_id: str) -> int:
        new_timestamp = int(datetime.now().timestamp())
        self._last_access_times[data_id] = new_timestamp
        return new_timestamp

    def remove(self, data_id: str):
        if data_id in self._datasets.keys():
            dataset: xarray.Dataset = self._datasets.pop(data_id)
            try:
                dataset.close()
            except:
                pass

            del dataset

        if data_id in self._last_access_times:
            del self._last_access_times[data_id]

    def __len__(self) -> int:
        return len(self._datasets)

    def keys(self) -> typing.Iterable[str]:
        return self._datasets.keys()

    def clean_up(self):
        while len(self._datasets) > self._limit:
            least_recent_id, timestamp = self._last_access_times.most_common()[-1]
            logging.debug(f"Too many data frames detected - removing {least_recent_id}")
            self.remove(least_recent_id)

    def clear(self):
        keys: list[str] = list(self._datasets.keys())

        for key in keys:
            self.remove(key)

        self._datasets = dict()
        self._last_access_times = Counter()

    def get(self, key: str) -> typing.Optional[xarray.Dataset]:
        if key not in self._datasets.keys():
            return None

        self.touch_frame(key)
        return self._datasets[key]
