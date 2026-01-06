"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import pathlib
import typing
from datetime import datetime

import pydantic
from pydantic import field_validator

from . import YanvRequest
from .base import YanvDataRequest
from yanv.messages.base import SpecificDataMessage
from ...utilities import DEFAULT_ROW_COUNT

_INDEX_TYPE = typing.Union[datetime, str, float, int]


class FileSelectionRequest(YanvRequest):
    """
    A message asking for a netcdf file at a given location
    """
    operation: typing.Literal['load'] = pydantic.Field(description="Description stating that this should be loading data")
    path: pathlib.Path = pydantic.Field(description="The path to the requested file")


class SampleRequest(YanvDataRequest):
    """
    A message asking for a sample of data
    """
    variable: str
    operation: typing.Literal['sample'] = pydantic.Field(description="Description stating that this will be asking for data")
    value_format: typing.Optional[str] = pydantic.Field(default=None, description="How values should be formatted")


class DataDescriptionRequest(YanvDataRequest):
    operation: typing.Literal['data_description'] = pydantic.Field(
        description="Description stating that this will be asking for descriptive statistics about data"
    )
    variable: str
    container_id: str

class FilterRequest(YanvDataRequest):
    """
    Request used to filter data
    """
    operation: typing.Literal['filter'] = pydantic.Field(
        description="Description stating that this is intended to filter data"
    )


class PageRequest(YanvDataRequest):
    """
    Request used to filter data
    """
    operation: typing.Literal['page'] = pydantic.Field(
        description="Description stating that this is intended to load a different page of data"
    )


class GroupOptionRequest(YanvDataRequest):
    """
    Request used to ask what is available to group data by
    """
    operation: typing.Literal['group_options'] = pydantic.Field(
        description="Description stating that this is intended to load a different page of data"
    )


class DataSpecificationDescription(pydantic.BaseModel):
    """
    Describes how specific data should be interpreted
    """
    dimension: str
    minimum: _INDEX_TYPE
    maximum: _INDEX_TYPE
    value: _INDEX_TYPE
    animate: typing.Optional[bool] = pydantic.Field(
        default=False,
        description="Indicates that this group separates frames of an animation"
    )


class PlotDataRequest(YanvDataRequest):
    """
    Request used to gather data within a range of groups
    """
    operation: typing.Literal['plot_data'] = pydantic.Field(
        description="Description stating that this is intended to plot data by at least one specification"
    )

    variable: str
    ranges: typing.Union[DataSpecificationDescription, typing.Sequence[DataSpecificationDescription]]

    def should_animate(self) -> bool:
        if isinstance(self.ranges, DataSpecificationDescription):
            return self.ranges.animate

        return any([specification.animate for specification in self.ranges])
