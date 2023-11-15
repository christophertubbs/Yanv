"""
Defines base classes for all messages
"""
from __future__ import annotations

import abc
import typing

import pydantic

from yanv.utilities import DEFAULT_ROW_COUNT
from yanv.utilities import DataFilter


class YanvMessage(pydantic.BaseModel, abc.ABC):
    """
    A common base class for all messages
    """
    operation: str = pydantic.Field(description="The name of the operation to perform")
    message_id: typing.Optional[str] = pydantic.Field(default=None, description="A trackable ID for the message")


class DataMessage(pydantic.BaseModel):
    data_id: str = pydantic.Field(description="The ID of the data to pass back and forth")


class SpecificDataMessage(DataMessage):
    page_number: int = pydantic.Field(description="What page of data to retrieve")
    columns: typing.Optional[typing.List[str]] = pydantic.Field(
        default=None,
        description="An explicit list of columns to return"
    )
    row_count: typing.Optional[int] = pydantic.Field(
        default=DEFAULT_ROW_COUNT,
        description="The number of rows to return"
    )
    filters: typing.Optional[typing.Sequence[DataFilter]] = pydantic.Field(
        default_factory=list,
        description="Filters used to reduce the data that is returned"
    )