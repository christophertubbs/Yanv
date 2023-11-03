"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from .base import YanvResponse
from ..base import DataMessage


class YanvDataResponse(DataMessage):
    data: typing.List[typing.Dict[str, typing.Any]] = pydantic.Field(description="The requested data")
    metadata: typing.Dict[str, typing.Any] = pydantic.Field(description="Metadata from the netcdf file")
    column_metadata: typing.Dict[str, typing.Dict[str, typing.Any]] = pydantic.Field(
        description="Information about each given column"
    )