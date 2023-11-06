"""
Defines error messages to return to clients
"""
from __future__ import annotations

import typing

import pydantic

from ..base import YanvMessage


class ErrorResponse(YanvMessage):
    error_message: str = pydantic.Field(description="A description of the error")
    message_type: typing.Optional[str] = pydantic.Field(
        default=None,
        description="The name of the type of message that caused the error"
    )


def invalid_message_response() -> ErrorResponse:
    return ErrorResponse(
        error_message="The received message was not valid JSON and/or could not be interpreted"
    )


def unrecognized_message_response() -> ErrorResponse:
    return ErrorResponse(
        error_message="The received message was not valid"
    )
