"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from .base import YanvResponse
from ..base import DataMessage
from ...model.dataset import Dataset


class YanvDataResponse(DataMessage):
    data: Dataset