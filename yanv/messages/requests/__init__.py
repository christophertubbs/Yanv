"""
Definitions for the type of messages that may be used to request data
"""
import inspect
import typing

import pydantic

from .base import YanvRequest

from .data import FileSelectionRequest
from .data import PageRequest
from ...utilities.common import get_subclasses


def get_message_types() -> typing.Tuple[typing.Type[YanvRequest], ...]:
    return tuple([message_type for message_type in get_subclasses(YanvRequest)])


class MasterRequest(pydantic.BaseModel):
    request: typing.Union[get_message_types()]