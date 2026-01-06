"""
Defines a backed that can load files
"""
import typing
import logging
import pathlib
from os import PathLike
import io
from urllib.parse import urlparse

import xarray
import requests

from yanv.backend.base import BaseBackend
from yanv.cache import CACHE_TYPE

LOGGER: logging.Logger = logging.getLogger(pathlib.Path(__file__).stem)


class FileBackend(BaseBackend):
    """
    A backend built to focus on loading data from the local file system
    """

    def clean(self) -> None:
        self.cache.clear()

    @property
    def cache(self) -> CACHE_TYPE:
        return self.__cache

    def load(self, path: PathLike, *args, **kwargs) -> str:
        """
        Load the data from disk. Load from the web and keep it in memory if an http address is passed

        Args:
            path: Where to find the data
            *args:
            **kwargs:

        Returns:
            The proper identifier to use to find the data within the backend
        """
        preexisting_id = self.__entry_record.get(path)

        # If the data already exists, just return that data
        if preexisting_id:
            frame = self.cache.get(preexisting_id)
            if frame:
                return preexisting_id

            # If the key was there but didn't bear any data, kill the key
            del self.__entry_record[path]

        parsed_url = urlparse(str(path))
        if parsed_url.scheme.startswith("http"):
            # Requesting data via web address will play foul with the address string by flipping forward slashes on
            # windows. Reverse received backslashes to create proper urls
            sanitized_path: str = parsed_url.path.replace("\\", "/")
            url = f"{parsed_url.scheme}:/{sanitized_path}"

            # Download the data and save within an in-memory dataset
            LOGGER.debug(f"Downloading data from {url}")
            with requests.get(url) as response:
                import pathlib
                buffer = io.BytesIO(response.content)
                buffer.seek(0)
                dataset = xarray.load_dataset(buffer, engine="h5netcdf")
                dataset.encoding['source'] = url
            LOGGER.debug(f"Data downloaded from {url}")
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
