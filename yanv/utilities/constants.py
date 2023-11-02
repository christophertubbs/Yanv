"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import enum
import typing

from yanv.utilities.base import TextValueEntry

DEFAULT_ROW_COUNT = 10


class Comparator(TextValueEntry, enum.Enum):
    GREATER_THAN = TextValueEntry(text=">", value="GREATER_THAN")
    GREATER_THAN_OR_EQUAL_TO = TextValueEntry(text=">=", value="GREATER_THAN_OR_EQUAL_TO")
    EQUAL_TO = TextValueEntry(text="==", value="EQUAL_TO")
    LESS_THAN_OR_EQUAL_TO = TextValueEntry(text="<=", value="LESS_THAN_OR_EQUAL_TO")
    LESS_THAN = TextValueEntry(text="<", value="LESS_THAN")
    NOT_EXISTS = TextValueEntry(text="Not Null", value="NOT_EXISTS")
    EXISTS = TextValueEntry(text="Exists", value="EXISTS")
    CONTAINS = TextValueEntry(text="Contains", value="CONTAINS")


class DataType(TextValueEntry, enum.Enum):
    INT = TextValueEntry(text="Integer", value="int", input_type="number")
    FLOAT = TextValueEntry(text="Floating Point", value="float", input_type="number")
    BOOL = TextValueEntry(text="Boolean", value="bool", input_type="checkbox")
    TIME = TextValueEntry(text="Time", value="time", input_type="time")
    DATE = TextValueEntry(text="Date", value="date", input_type="date")
    DATETIME = TextValueEntry(text="Date and Time", value="datetime", input_type="datetime-local")
    STRING = TextValueEntry(text="String", value="str", input_type="text")