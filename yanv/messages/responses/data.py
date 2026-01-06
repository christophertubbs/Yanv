"""
Types of responses pertaining to data
"""
import typing

import pydantic

from yanv.messages.responses.base import YanvResponse
from ..base import DataMessage
from yanv.model.dataset import Dataset


class YanvDataResponse(YanvResponse, DataMessage):
    data: Dataset


class YanvSampleResponse(YanvResponse, DataMessage):
    samples: list[str]


class DataDescriptionResponse(YanvResponse, DataMessage):
    container_id: str
    variable: str
    minimum: typing.Optional[str] = pydantic.Field(default=None, description="The minimum value in the data")
    maximum: typing.Optional[str] = pydantic.Field(default=None, description="The maximum value in the data")
    mean: typing.Optional[str] = pydantic.Field(default=None, description="The mean value of the data")
    median: typing.Optional[str] = pydantic.Field(default=None, description="The median value of the data")
    std: typing.Optional[str] = pydantic.Field(default=None, description="The standard deviation of the data")
    samples: list[str] = pydantic.Field(default_factory=list, description="Examples of values from within the variable")
    count: int = pydantic.Field(default=0, description="The number of items in the variable")


class PlotDataResponse(YanvResponse, DataMessage):
    operation: typing.Literal["plot_data"]
    markup: str
