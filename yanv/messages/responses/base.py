"""
@TODO: Put a module wide description here
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


class AcknowledgementResponse(YanvResponse):
    operation: typing.Literal['acknowledgement'] = pydantic.Field(default="acknowledgement")