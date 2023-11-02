"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic

from yanv.utilities.constants import Comparator


class DataFilter(pydantic.BaseModel):
    field: str = pydantic.Field(description="The field to filter on")
    operator: Comparator = pydantic.Field(description="The operation to filter by")
    value: typing.Any = pydantic.Field(description="The value of the field to filter in relation to")