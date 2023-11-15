"""
Defines base classes for request messages
"""
from __future__ import annotations
from abc import ABC

from ..base import DataMessage
from ..base import YanvMessage


class YanvRequest(YanvMessage, ABC):
    ...


class YanvDataRequest(YanvRequest, DataMessage, ABC):
    ...