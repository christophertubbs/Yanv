"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib
import typing

import pydantic

from ..base import DataMessage
from ..base import YanvMessage
from ...utilities import DEFAULT_ROW_COUNT


class FileSelectionRequest(YanvMessage):
    """
    A message asking for a netcdf file at a given location
    """
    operation: typing.Literal['load'] = pydantic.Field(description="Description stating that this should be loading data")
    path: pathlib.Path = pydantic.Field(description="The path to the requested file")
    row_count: typing.Optional[int] = pydantic.Field(
        default=DEFAULT_ROW_COUNT,
        description="The number of rows to return"
    )


class FilterRequest(DataMessage):
    """
    Request used to filter data
    """
    operation: typing.Literal['filter'] = pydantic.Field(description="Description stating that this is intended to filter data")


class PageRequest(DataMessage):
    """
    Request used to filter data
    """
    operation: typing.Literal['page'] = pydantic.Field(
        description="Description stating that this is intended to load a different page of data"
    )