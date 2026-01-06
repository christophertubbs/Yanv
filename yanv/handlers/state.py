"""
The objects necessary to structure application state
"""
import typing
import dataclasses
import sys

import pandas

from yanv.backend.base import BaseBackend
from yanv.backend.file import FileBackend


@dataclasses.dataclass
class SocketState:
    """
    Contains state information meant to be persisted between socket messages on an active connection
    """
    backend: BaseBackend = dataclasses.field(default_factory=FileBackend)
    frames: typing.Dict[str, pandas.DataFrame] = dataclasses.field(default_factory=list)

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
