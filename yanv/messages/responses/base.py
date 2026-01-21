"""
Defines basic response classes
"""
from __future__ import annotations

import abc
import typing

import pydantic

from ..base import DataMessage
from ..base import YanvMessage


class YanvResponse(YanvMessage):
    ...


class OpenResponse(YanvResponse):
    operation: typing.Literal['connection_opened'] = pydantic.Field(default="connection_opened")


class RenderResponse(YanvResponse):
    markup: str
    container_id: str
    operation: typing.Literal['render'] = pydantic.Field(default="render")
    position: typing.Literal["child", "sibling"] = pydantic.Field(default="child")


class AcknowledgementResponse(YanvResponse):
    operation: typing.Literal['acknowledgement'] = pydantic.Field(default="acknowledgement")
