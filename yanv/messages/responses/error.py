"""
Defines error messages to return to clients
"""
from __future__ import annotations

import typing

import pydantic

from . import YanvResponse
from ..base import YanvMessage


class ErrorResponse(YanvResponse):
    def __init__(self, operation: str = "error", **kwargs):
        if 'operation' in kwargs and 'message_type' not in kwargs:
            kwargs['message_type'] = kwargs['operation']

        kwargs['operation'] = operation
        super().__init__(**kwargs)

    error_message: str = pydantic.Field(description="A description of the error")
    message_type: typing.Optional[str] = pydantic.Field(
        default=None,
        description="The name of the type of message that caused the error"
    )


def invalid_message_response() -> ErrorResponse:
    return ErrorResponse(
        error_message="The received message was not valid JSON and/or could not be interpreted"
    )


def missing_data_response(data_id: str) -> ErrorResponse:
    return ErrorResponse(
        f"No data could be found with an id of '{data_id}'"
    )


def unrecognized_message_response() -> ErrorResponse:
    return ErrorResponse(
        error_message="The received message was not valid"
    )
