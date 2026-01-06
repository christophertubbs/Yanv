"""
Basic mixins that may be used across the code base
"""
import typing
import contextlib
import collections.abc as generic

from threading import Lock
from threading import RLock


class Lockable:
    """
    An object that may be locked
    """
    @property
    def _lock(self) -> RLock:
        if not hasattr(self, "_lock_"):
            self._lock_ = RLock()
        return self._lock_

    def acquire(self, blocking: bool = True, timeout: float = -1) -> None:
        """Acquire the lock on the object"""
        self._lock.acquire(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        """Release the lock on the object"""
        self._lock.release()

    def __enter__(self) -> typing.Self:
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    @contextlib.contextmanager
    def lock(self, *values: typing.Any, **named_values: typing.Any) -> generic.Iterator[None]:
        with self.lock_all(self, *values, **named_values):
            yield

    @classmethod
    @contextlib.contextmanager
    def lock_all(cls, *values: typing.Any, **named_values: typing.Any) -> generic.Iterator[None]:
        organized_lock_targets: dict[int, Lockable | RLock] = {}

        for value in values:
            if isinstance(value, (Lock, RLock, Lockable)):
                organized_lock_targets[id(value)] = value

        for value in named_values.values():
            if isinstance(value, (Lock, RLock, Lockable)):
                organized_lock_targets[id(value)] = value

        ordered_locks: list[Lock | RLock | Lockable] = sorted(
            organized_lock_targets.values(),
            key=id
        )

        with contextlib.ExitStack() as exit_stack:
            for lock in ordered_locks:
                exit_stack.enter_context(lock)
            yield
