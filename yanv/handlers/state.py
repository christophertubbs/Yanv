"""
The objects necessary to structure application state
"""
import typing
import dataclasses
import sys
import weakref

import pandas

from aiohttp.web import Request

from yanv.backend.base import BaseBackend
from yanv.backend.file import FileBackend


@dataclasses.dataclass
class SocketState:
    """
    Contains state information meant to be persisted between socket messages on an active connection
    """
    backend: BaseBackend = dataclasses.field(default_factory=FileBackend)
    frames: typing.Dict[str, pandas.DataFrame] = dataclasses.field(default_factory=list)
    _request: typing.Optional[weakref.ref[Request] | Request] = dataclasses.field(
        default=None,
        repr=False,
        compare=False,
        kw_only=True,
    )

    def __post_init__(self):
        if self._request is not None and not isinstance(self._request, weakref.ReferenceType):
            self._request = weakref.ref(self._request)

    @property
    def request(self) -> typing.Optional[Request]:
        return self._request()

    @request.setter
    def request(self, value: Request | weakref.ref[Request]):
        if isinstance(value, Request):
            self._request = weakref.ref(value)
        if isinstance(value, weakref.ReferenceType) and isinstance(value(), Request):
            self._request = value
        raise TypeError(f"Cannot set the Request that launched the socket's state - it is not a Request")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        keys: list[str] = list(self.frames.keys())

        for identifier in keys:
            try:
                data = self.frames.pop(identifier, None)

                if data is not None:
                    try:
                        del data
                    except Exception as e:
                        pass
            except Exception as e:
                print(f"Could not remove the data with the identifier of {identifier}", file=sys.stderr)
