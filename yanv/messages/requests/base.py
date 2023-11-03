"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import abc
import typing

import pydantic

from ..base import DataMessage
from ..base import YanvMessage


class YanvRequest(YanvMessage):
    ...


class YanvDataRequest(DataMessage):
    ...