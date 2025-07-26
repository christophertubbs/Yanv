"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing
from os import PathLike
import io
from urllib.parse import urlparse

import pandas
import xarray
import requests

from yanv.backend.base import BaseBackend
from yanv.cache import CACHE_TYPE


class FileBackend(BaseBackend):
    @property
    def cache(self) -> CACHE_TYPE:
        return self.__cache

    def load(self, path: PathLike, *args, **kwargs) -> str:
        preexisting_id = self.__entry_record.get(path)

        if preexisting_id:
            frame = self.cache.get(preexisting_id)
            if frame:
                return preexisting_id
            del self.__entry_record[path]

        parsed_url = urlparse(str(path))
        if parsed_url.scheme.startswith("http"):
            url = f"{parsed_url.scheme}:/{parsed_url.path.replace("\\", "/")}"
            with requests.get(url) as response:
                import pathlib
                buffer = io.BytesIO(response.content)
                buffer.seek(0)
                dataset = xarray.load_dataset(buffer, engine="h5netcdf")
                dataset.encoding['source'] = url
                #new_path: pathlib.Path = pathlib.Path("store") / pathlib.Path(path).name
                #with open(new_path, "wb") as new_file:
                #    new_file.write(response.content)
                #path = new_path
        else:
            dataset = xarray.load_dataset(path)

        data_id = self.cache.add(dataset)
        self.__entry_record[path] = data_id

        return data_id

    def __init__(self, cache: CACHE_TYPE = None):
        if cache:
            self.__cache = cache
        else:
            self.__cache = self.get_default_cache()

        self.__entry_record: typing.Dict[PathLike, str] = dict()
