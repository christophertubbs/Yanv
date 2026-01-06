"""
Defines the base class for the cache that will store loaded xarray data
"""
import abc
import typing
import random
import string
import collections.abc as generic

import pandas
import xarray

from yanv.model.dataset import Dataset
from yanv.utilities.collections import SafeSet

_DATA_ID_LENGTH = 5
_DATA_ID_CHARACTER_SET = string.hexdigits

H = typing.TypeVar("H", bound=generic.Hashable)


class IDGenerator:
    def __init__(self, id_length: int = _DATA_ID_LENGTH, character_set: str = _DATA_ID_CHARACTER_SET):
        self.id_length: int = id_length
        self.character_set: str = character_set
        self.generated_ids: SafeSet[str] = SafeSet()

    def _build_id(self) -> str:
        return ''.join(random.choices(population=self.character_set, k=self.id_length))

    def generate_id(self) -> str:
        new_id: str = self._build_id()

        while new_id in self.generated_ids:
            new_id = self._build_id()

        self.generated_ids.add(new_id)
        return new_id


ID_GENERATOR: IDGenerator = IDGenerator()


class DatasetCache(abc.ABC):
    """
    The interface for a mechanism that keeps xarray datasets available in memory

    Needed since standard caching does not support xarray datasets well, if not at all
    """
    @staticmethod
    def _generate_data_id() -> str:
        """
        Generate a unique ID to tag data with
        """
        return ID_GENERATOR.generate_id()

    def get_information(self, key: str) -> typing.Optional[Dataset]:
        """
        Try to get a dataset summary by its ID

        Args:
            key: The ID issued when the desired dataset was added to the cache

        Returns:
            The retrieved dataset
        """
        dataset = self.get(key=key)
        return Dataset.from_xarray(dataset) if dataset else None

    def get_frame(self, key: str) -> typing.Optional[pandas.DataFrame]:
        """
        Try to get a dataset in pandas DataFrame form by its ID

        Args:
            key: The ID of the data that had been cached

        Returns:
            A pandas dataframe if there is a frame with that key
        """
        dataset = self.get(key)
        return dataset.to_dataframe() if isinstance(dataset, xarray.Dataset) else None

    @abc.abstractmethod
    def add(self, data: xarray.Dataset):
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
    def get(self, key: str) -> typing.Optional[xarray.Dataset]:
        ...


CACHE_TYPE = typing.TypeVar("CACHE_TYPE", bound=DatasetCache, covariant=True)
