"""
Handling for messages comming through a websocket
"""
from __future__ import annotations

import json
import logging
import random
import string
import typing
import pathlib
import os

import numpy.random
from aiohttp import WSMessage
from aiohttp import web
from aiohttp_jinja2 import render_string

from yanv.messages.responses import invalid_message_response
from yanv.messages.responses.error import missing_data_response
from yanv.utilities.common import local_only
from yanv.messages.base import YanvMessage
from yanv.messages.requests import FileSelectionRequest
from yanv.messages.requests.data import DataDescriptionRequest
from yanv.messages.responses.base import RenderResponse
from yanv.messages.requests import MasterRequest
from yanv.messages.requests import YanvRequest
from yanv.messages.responses import ErrorResponse
from yanv.messages.responses.base import OpenResponse
from yanv.messages.responses.data import YanvDataResponse
from yanv.messages.responses.data import DataDescriptionResponse

from yanv.handlers.state import SocketState

CONNECTION_ID_LENGTH = 10
CONNECTION_ID_CHARACTER_SET = string.hexdigits

REQUEST_TYPE = typing.TypeVar("REQUEST_TYPE", bound=YanvRequest, covariant=True)
RESPONSE_TYPE = typing.TypeVar("RESPONSE_TYPE", bound=YanvMessage, covariant=True)

LOGGER: logging.Logger = logging.getLogger(pathlib.Path(__file__).stem)


HANDLER = typing.Callable[[REQUEST_TYPE, SocketState], RESPONSE_TYPE]


def load_file(request: FileSelectionRequest, state: SocketState) -> YanvDataResponse:
    """
    Handles the request to load a file

    Args:
        request: A request asking for a specific file
        state: The current state of the data that has flown through the given socket

    Returns:
        A response object ready to send back to the client
    """
    new_id: str = state.backend.load(request.path)
    uploaded_data = state.backend.cache.get_information(new_id)

    response = YanvDataResponse(
        operation=request.operation,
        data_id=new_id,
        data=uploaded_data,
        message_id=request.message_id
    )

    return response


def describe_data(request: DataDescriptionRequest, state: SocketState) -> RenderResponse | ErrorResponse:
    """
    Read information from a variable and generate a description of it

    Args:
        request:
        state:

    Returns:
        A response bearing important information, such as summary statistics
    """
    import pandas
    import xarray
    from numpy import dtypes
    import numpy

    dataset: xarray.Dataset | None = state.backend.cache.get(key=request.data_id)

    if dataset is None:
        return missing_data_response(data_id=request.data_id)

    if request.variable not in dataset:
        return ErrorResponse(
            message_id=request.message_id,
            error_message=f"There is no '{request.variable}' variable within dataset {request.data_id}",
        )

    data: xarray.DataArray = dataset[request.variable]

    if 'valid_range' in data.attrs and isinstance(data.attrs['valid_range'], typing.Iterable):
        try:
            lower_limit = min(data.attrs['valid_range'])
            upper_limit = max(data.attrs['valid_range'])
            data = data.where((lower_limit < data) & (data < upper_limit), drop=True)
        except Exception as e:
            LOGGER.error(f"Could not constrain '{request.variable}' to its valid range: {e}")

    context: dict[str, typing.Optional[str | typing.Sequence[str]]] = {
        "minimum": "NaN",
        "maximum": "NaN",
        "mean": "NaN",
        "median": "NaN",
        "samples": [],
        "count": str(data.size),
        "std": "NaN",
        "data_id": request.data_id,
        "message_id": request.message_id,
        "variable": request.variable,
    }

    if not isinstance(data.dtype, (dtypes.ObjectDType, dtypes.BytesDType, dtypes.StrDType)) and len(data.shape) > 0:
        try:
            minimum = data.min().values

            if issubclass(minimum.dtype.type, float):
                minimum = f"{minimum:.2f}"
            else:
                minimum = str(minimum)

            context['minimum'] = minimum
        except Exception as e:
            LOGGER.error(f"Could not calculate the minimum of '{data.dtype} {request.variable}': {e}")

    if not isinstance(data.dtype, (dtypes.ObjectDType, dtypes.BytesDType, dtypes.StrDType)) and len(data.shape) > 0:
        try:
            maximum = data.max().values

            if issubclass(maximum.dtype.type, float):
                maximum = f"{maximum:.2f}"
            else:
                maximum = str(maximum)
            context['maximum'] = maximum
        except Exception as e:
            LOGGER.error(f"Could not calculate the maximum of '{data.dtype} {request.variable}': {e}")

    if not isinstance(data.dtype, (dtypes.ObjectDType, dtypes.BytesDType, dtypes.StrDType, dtypes.DateTime64DType)) and len(data.shape) > 0:
        try:
            std = data.std().values

            if issubclass(std.dtype.type, float):
                std = f"{std:.2f}"
            else:
                std = str(std)
            context['std'] = std
        except Exception as e:
            LOGGER.error(f"Could not calculate the standard deviation of '{data.dtype} {request.variable}': {e}")

    if not isinstance(data.dtype, (dtypes.ObjectDType, dtypes.BytesDType, dtypes.StrDType)) and len(data.shape) > 0:
        try:
            mean = data.mean().values

            if issubclass(mean.dtype.type, float):
                mean = f"{mean:.2f}"
            else:
                mean = str(mean)
            context['mean'] = mean
        except Exception as e:
            LOGGER.error(f"Could not calculate the mean of '{data.dtype} {request.variable}': {e}")

    if not isinstance(data.dtype, (dtypes.ObjectDType, dtypes.BytesDType, dtypes.StrDType, dtypes.DateTime64DType)) and len(data.shape) > 0:
        try:
            median = data.median().values

            if issubclass(median.dtype.type, float):
                median = f"{median:.2f}"
            else:
                median = str(median)
            context['median'] = median
        except Exception as e:
            LOGGER.error(f"Could not calculate the median of '{data.dtype} {request.variable}': {e}")

    try:
        non_nan_data: xarray.DataArray = data.where(data.notnull(), drop=True)
        if non_nan_data.size > 0:
            sample_count: int = min(5, non_nan_data.size)
            sample = [
                f"{value:.2f}" if issubclass(non_nan_data.dtype.type, float) else str(value)
                for value in numpy.random.choice(non_nan_data.values.ravel(), size=sample_count, replace=False)
            ]
            context['samples'] = sample
    except Exception as e:
        LOGGER.error(f"Could not sample '{data.dtype} {request.variable}': {e}")

    markup: str = render_string(
        template_name="variable_summary.html",
        request=state.request,
        context=context
    )

    response: RenderResponse = RenderResponse(
        message_id=request.message_id,
        markup=markup,
        container_id=request.container_id,
    )

    return response


MESSAGE_HANDLERS: typing.Mapping[typing.Type[REQUEST_TYPE], typing.Union[HANDLER, typing.Sequence[HANDLER]]] = {
    FileSelectionRequest: load_file,
    DataDescriptionRequest: describe_data
}


def default_message_handler(request: YanvRequest, state: SocketState) -> RESPONSE_TYPE:
    """
    Process a message with no real handler that just sends back a recognition that information was communicated

    Args:
        request: The request from the client
        state: The current state information for the socket

    Returns:
        A generic response acknowledging communication
    """
    message_type: str = type(request).__qualname__
    message: str = f"There are no handlers for the '{request.operation}' operation requested from a {message_type}"
    LOGGER.error(message, stack_info=True)
    return ErrorResponse(
        error_message=f"There are no handlers for the '{request.operation}' operation",
        message_type=message_type,
        message_id=request.message_id
    )


async def handle_message(
    connection: web.WebSocketResponse,
    message: typing.Union[str, bytes, dict],
    state: SocketState,
) -> None:
    """
    Handle a raw message that has come in from a client

    Args:
        connection: The connection through which information may flow
        message: The raw data that prompted handling
        state: The current state of the application for a user's connection
    """
    if isinstance(message, (str, bytes)):
        message = json.loads(message)

    request: typing.Optional[YanvRequest] = None
    responses: list[YanvMessage] = []
    failed: bool = False

    try:
        request_wrapper = MasterRequest.model_validate({"request": message})
        request = request_wrapper.request
    except Exception as error:
        LOGGER.error(
            f"Could not deserialize the incoming message due to: {error}{os.linesep * 2}{message}{os.linesep * 2}",
            exc_info=True
        )
        responses.append(invalid_message_response())
        failed = True

    if not failed and isinstance(request, YanvRequest):
        try:
            handler = MESSAGE_HANDLERS.get(type(request), default_message_handler)

            if isinstance(handler, typing.Sequence):
                handlers: typing.Sequence[HANDLER] = handler
            else:
                handlers: typing.Sequence[HANDLER] = [handler]

            for function in handlers:
                responses.append(function(request, state))

            if not responses:
                responses.append(default_message_handler(request, state))

        except BaseException as error:
            message = f"An error occurred while handling a `{type(request).__name__}` message: {str(error)}"
            LOGGER.error(
                message,
                exc_info=error,
                stack_info=True
            )
            response = ErrorResponse(
                message_id=request.message_id,
                message_type=type(request).__name__,
                error_message=message
            )
            responses.append(response)
    elif not failed:
        LOGGER.error(
            f"The data sent from the client was a proper request but did not bear a proper inner request:{os.linesep}"
        )
        response = invalid_message_response()
        responses.append(response)

    for response in responses:
        await connection.send_json(response.model_dump())


@local_only
async def socket_handler(request: web.Request) -> web.WebSocketResponse:
    """
    Handle information coming in through a websocket connection

    Args:
        request: The request to form the connection

    Returns:
        The connection that was made with the client
    """
    connection = web.WebSocketResponse()

    # Come up with a basic ID to help track when connections are opening or closing
    connection_id = ''.join(random.choices(population=CONNECTION_ID_CHARACTER_SET, k=CONNECTION_ID_LENGTH))

    await connection.prepare(request=request)

    # Create a container for state information that will hold application state for this socket connection
    state = SocketState(_request=request)

    LOGGER.info(f"Connected to socket {connection_id} from {request.remote}")

    # Prepare and send a response saying "You have been connected to the application
    open_response = OpenResponse()
    await connection.send_json(open_response.model_dump())

    # Handle messages as they come through the connection
    async for message in connection:  # type: WSMessage
        await handle_message(connection, message=message.data, state=state)

    LOGGER.info(f"Connection to Socket {connection_id} closing")

    return connection
