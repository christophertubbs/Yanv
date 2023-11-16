"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import json
import logging
import random
import string
import typing
from dataclasses import dataclass
from dataclasses import field
from pprint import pprint

import pandas
from aiohttp import WSMessage
from aiohttp import web

from yanv.messages.responses import invalid_message_response
from yanv.utilities.common import local_only
from yanv.backend.base import BaseBackend
from yanv.backend.file import FileBackend
from yanv.messages.base import YanvMessage
from yanv.messages.requests import FileSelectionRequest
from yanv.messages.requests import MasterRequest
from yanv.messages.requests import YanvRequest
from yanv.messages.responses import ErrorResponse
from yanv.messages.responses.base import AcknowledgementResponse
from yanv.messages.responses.base import OpenResponse
from yanv.messages.responses.data import YanvDataResponse

CONNECTION_ID_LENGTH = 10
CONNECTION_ID_CHARACTER_SET = string.hexdigits

REQUEST_TYPE = typing.TypeVar("REQUEST_TYPE", bound=YanvRequest, covariant=True)
RESPONSE_TYPE = typing.TypeVar("RESPONSE_TYPE", bound=YanvMessage, covariant=True)


@dataclass
class SocketState:
    backend: BaseBackend = field(default_factory=FileBackend)
    frames: typing.Dict[str, pandas.DataFrame] = field(default_factory=list)


HANDLER = typing.Callable[[REQUEST_TYPE, SocketState], RESPONSE_TYPE]


def load_file(request: FileSelectionRequest, state: SocketState) -> YanvDataResponse:
    new_id = state.backend.load(request.path)
    uploaded_data = state.backend.cache.get_information(new_id)

    response = YanvDataResponse(
        operation=request.operation,
        data_id=new_id,
        data=uploaded_data,
        message_id=request.message_id
    )

    return response


MESSAGE_HANDLERS: typing.Mapping[typing.Type[REQUEST_TYPE], typing.Union[HANDLER, typing.Sequence[HANDLER]]] = {
    FileSelectionRequest: load_file
}


def default_message_handler(request: YanvRequest, state: SocketState) -> RESPONSE_TYPE:
    return AcknowledgementResponse(message_id=request.message_id)


async def handle_message(connection: web.WebSocketResponse, message: typing.Union[str, bytes, dict], state: SocketState):
    if isinstance(message, (str, bytes)):
        message = json.loads(message)

    request: typing.Optional[YanvRequest] = None
    response = None

    try:
        request_wrapper = MasterRequest.model_validate({"request": message})
        request = request_wrapper.request
    except Exception as error:
        print(error)
        print("Could not deserialize incoming message:")
        pprint(message)
        response = invalid_message_response()

    if isinstance(request, YanvRequest):
        try:
            handler = MESSAGE_HANDLERS.get(type(request), default_message_handler)

            if isinstance(handler, typing.Sequence):
                handlers: typing.Sequence[HANDLER] = handler
            else:
                handlers: typing.Sequence[HANDLER] = [handler]

            for function in handlers:
                response = function(request, state)

            if response is None:
                response = default_message_handler(request, state)

        except BaseException as error:
            message = f"An error occurred while handling a `{type(request).__name__}` message: {str(error)}"
            logging.error(
                message,
                exc_info=error,
                stack_info=True
            )
            response = ErrorResponse(
                message_id=request.message_id,
                message_type=type(request).__name__,
                error_message=message
            )

    await connection.send_json(response.model_dump())


@local_only
async def socket_handler(request: web.Request) -> web.WebSocketResponse:
    connection = web.WebSocketResponse()

    connection_id = ''.join(random.choices(population=CONNECTION_ID_CHARACTER_SET, k=CONNECTION_ID_LENGTH))

    await connection.prepare(request=request)
    state = SocketState()

    print(f"Connected to socket {connection_id} from {request.remote}")

    open_response = OpenResponse()

    await connection.send_json(open_response.model_dump())

    async for message in connection:  # type: WSMessage
        await handle_message(connection, message=message.data, state=state)

    print(f"Connection to Socket {connection_id} closing")

    return connection