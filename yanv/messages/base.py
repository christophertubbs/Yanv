"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing
from datetime import datetime

import pydantic

from yanv.utilities import DEFAULT_ROW_COUNT
from yanv.utilities import DataFilter


class YanvMessage(abc.ABC, pydantic.BaseModel):
    """
    A common base class for all messages
    """
    operation: str = pydantic.Field(description="The name of the operation to perform")
    message_id: typing.Optional[str] = pydantic.Field(default=None, description="A trackable ID for the message")
    message_time: typing.Optional[datetime] = pydantic.Field(
        default=datetime.now().astimezone(),
        description="When this message was first encountered"
    )


class DataMessage(abc.ABC, YanvMessage):
    data_id: str = pydantic.Field(description="The ID of the data to pass back and forth")
    columns: typing.Optional[typing.List[str]] = pydantic.Field(
        default=None,
        description="An explicit list of columns to return"
    )


class SpecificDataMessage(abc.ABC, DataMessage):
    page_number: int = pydantic.Field(description="What page of data to retrieve")
    row_count: typing.Optional[int] = pydantic.Field(
        default=DEFAULT_ROW_COUNT,
        description="The number of rows to return"
    )
    filters: typing.Optional[typing.Sequence[DataFilter]] = pydantic.Field(
        default_factory=list,
        description="Filters used to reduce the data that is returned"
    )