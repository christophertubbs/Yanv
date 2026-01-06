"""
Implementations for custom collections
"""
import typing
import collections.abc as generic

from yanv.utilities.mixins import Lockable

H = typing.TypeVar("H", bound=typing.Hashable)


class SafeSet(Lockable, generic.MutableSet[H]):
    """A thread-safe set"""
    def __init__(self, items: generic.Iterable[H] = None):
        """
        Build an unordered collection of unique elements.
        # (copied from class doc)
        """
        self.__inner_set: set[H] = set(items or tuple())

    def add(self, value: H, /) -> None:
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """
        with self:
            self.__inner_set.add(value)

    def clear(self) -> None:
        """ Remove all elements from this set. """
        with self:
            self.__inner_set.clear()

    def copy(self):
        """ Return a shallow copy of a set. """
        with self:
            snapshot: set[H] = self.__inner_set.copy()
        return self.__class__(snapshot)

    def difference(self, *value: generic.Iterable[H]):
        """ Return a new set with elements in the set that are not in the others. """
        for position, iterable in enumerate(value):
            if not isinstance(iterable, generic.Iterable):
                raise TypeError(
                    f"value at position {position}: '{repr(iterable)}' (type={type(iterable)}) is not iterable. "
                    f"A difference may not be formed."
                )
        with self.lock(*value):
            return self.__class__(self.__inner_set.difference(*value))

    def difference_update(self, *value: generic.Iterable[H]) -> None:
        """ Update the set, removing elements found in others. """
        for position, iterable in enumerate(value):
            if not isinstance(iterable, generic.Iterable):
                raise TypeError(
                    f"value at position {position}: '{repr(iterable)}' (type={type(iterable)}) is not iterable. "
                    f"A difference may not be formed."
                )
        with self.lock(*value):
            self.__inner_set.difference_update(*value)

    def discard(self, value: H, /) -> None:
        """
        Remove an element from a set if it is a member.

        Unlike set.remove(), the discard() method does not raise
        an exception when an element is missing from the set.
        """
        with self:
            self.__inner_set.discard(value)

    def intersection(self, *value: generic.Iterable[H]) -> "SafeSet[H]":
        """ Return a new set with elements common to the set and all others. """
        for position, iterable in enumerate(value):
            if not isinstance(iterable, generic.Iterable):
                raise TypeError(
                    f"value at position {position}: '{repr(iterable)}' (type={type(iterable)}) is not iterable. "
                    f"Intersection may not be formed."
                )

        with self.lock(*value):
            return self.__class__(self.__inner_set.intersection(*value))

    def intersection_update(self, *value: generic.Iterable[H]) -> None:
        """ Update the set, keeping only elements found in it and all others. """
        for position, iterable in enumerate(value):
            if not isinstance(iterable, generic.Iterable):
                raise TypeError(
                    f"value at position {position}: '{repr(iterable)}' (type={type(iterable)}) is not iterable. "
                    f"{self.__class__.__qualname__} cannot be updated via the intersection."
                )

        with self.lock(*value):
            return self.__inner_set.intersection_update(*value)

    def isdisjoint(self, value: generic.Iterable[H], /):
        """ Return True if two sets have a null intersection. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            return self.__inner_set.isdisjoint(value)

    def issubset(self, value: generic.Iterable[H], /) -> bool:
        """ Report whether another set contains this set. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            return self.__inner_set.issubset(value)

    def issuperset(self, value: generic.Iterable[H], /) -> bool:
        """ Report whether this set contains another set. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            return self.__inner_set.issuperset(value)

    def pop(self) -> H:
        """
        Remove and return an arbitrary set element.

        Raises KeyError if the set is empty.
        """
        with self:
            return self.__inner_set.pop()

    def remove(self, value: H, /) -> None:
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        with self:
            self.__inner_set.remove(value)

    def symmetric_difference(self, value: generic.Iterable[H], /) -> "SafeSet[H]":
        """ Return a new set with elements in either the set or other but not both. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")

        with self.lock(value):
            return self.__class__(self.__inner_set.symmetric_difference(value))

    def symmetric_difference_update(self, value: generic.Iterable[H], /) -> None:
        """ Update the set, keeping only elements found in either set, but not in both. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            return self.__inner_set.symmetric_difference_update(value)

    def union(self, *value: generic.Iterable[H]) -> "SafeSet[H]":
        """ Return a new set with elements from the set and all others. """
        for position, iterable in enumerate(value):
            if not isinstance(iterable, generic.Iterable):
                raise TypeError(
                    f"value at position {position}: '{repr(iterable)}' (type={type(iterable)}) is not iterable. "
                    f"A union may not be formed."
                )
        with self.lock(*value):
            return self.__class__(self.__inner_set.union(*value))

    def update(self, value: generic.Iterable[H], /) -> None:
        """ Update the set, adding elements from all others. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")

        with self.lock(value):
            if isinstance(value, SafeSet):
                self.__inner_set.update(value.__inner_set)
            else:
                self.__inner_set.update(value)

    def __and__(self, value: typing.Any, /) -> "SafeSet[H]":
        """ Return self&value. """
        with self.lock(value):
            if isinstance(value, SafeSet):
                return self.__class__(self.__inner_set & value.__inner_set)
            return self.__class__(self.__inner_set & value)

    def __contains__(self, value: H, /) -> bool:
        """ x.__contains__(y) <==> y in x. """
        with self:
            return value in self.__inner_set

    def __eq__(self, value: typing.Any, /) -> bool:
        """ Return self==value. """
        if isinstance(value, SafeSet):
            with self.lock(value):
                return self.__inner_set == value.__inner_set

        with self:
            return self.__inner_set == value

    def __ge__(self, value: typing.Any, /) -> bool:
        """ Return self>=value. """
        if isinstance(value, SafeSet):
            with self.lock(value):
                return self.__inner_set >= value.__inner_set

        with self:
            return self.__inner_set >= value

    def __gt__(self, value: typing.Any, /) -> bool:
        """ Return self>value. """
        if isinstance(value, SafeSet):
            with self.lock(value):
                return self.__inner_set > value.__inner_set

        with self:
            return self.__inner_set > value

    def __iand__(self, value: generic.Iterable[H], /) -> typing.Self:
        """ Return self|=value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        if isinstance(value, SafeSet):
            with self.lock(value):
                self.__inner_set &= value.__inner_set
                return self

        with self:
            if not isinstance(value, set):
                value = set(value)
            self.__inner_set &= value
            return self

    def __ior__(self, value: generic.Iterable[H], /) -> typing.Self:
        """ Return self|=value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")

        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            elif not isinstance(value, set):
                value = set(value)
            self.__inner_set |= value
            return self

    def __isub__(self, value: generic.Iterable[H], /) -> typing.Self:
        """ Return self-=value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")

        with self.lock(value):
            if isinstance(value, SafeSet):
                self.__inner_set -= value.__inner_set
                return self

            if not isinstance(value, set):
                value = set(value)

            self.__inner_set -= value
            return self

    def __iter__(self) -> generic.Iterator[H]:
        """ Implement iter(self). """
        with self:
            contents: list[H] = list(self.__inner_set)
        return iter(contents)

    def __ixor__(self, value: generic.Iterable[H], /) -> typing.Self:
        """ Return self^=value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            elif not isinstance(value, set):
                value = set(value)
            self.__inner_set ^= value
            return self

    def __len__(self) -> int:
        """ Return len(self). """
        with self:
            return len(self.__inner_set)

    def __le__(self, value: typing.Any, /) -> bool:
        """ Return self<=value. """
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            return self.__inner_set <= value

    def __lt__(self, value: typing.Any, /) -> bool:
        """ Return self<value. """
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            return self.__inner_set < value

    def __ne__(self, value: typing.Any, /) -> bool:
        """ Return self!=value. """
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            return self.__inner_set != value

    def __or__(self, value: typing.Any, /) -> "SafeSet[H]":
        """ Return self|value. """
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            return self.__class__(self.__inner_set | value)

    def __rand__(self, value: typing.Any, /) -> bool:
        """ Return value&self. """
        with self.lock(value):
            return value & self.__inner_set

    def __reduce__(self):
        """ Return state information for pickling. """
        with self:
            return self.__class__, (tuple(self.__inner_set),)

    def __repr__(self):
        """ Return repr(self). """
        with self:
            return repr(self.__inner_set)

    def __ror__(self, value: typing.Any, /):
        """ Return value|self. """
        with self.lock(value):
            return value | self.__inner_set

    def __rsub__(self, value: typing.Any, /):
        """ Return value-self. """
        with self.lock(value):
            return value - self.__inner_set

    def __rxor__(self, value: typing.Any, /):
        """ Return value^self. """
        with self.lock(value):
            return value ^ self.__inner_set

    def __sub__(self, value: generic.Iterable[H], /) -> "SafeSet[H]":
        """ Return self-value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            if isinstance(value, SafeSet):
                value: set[H] = value.__inner_set
            elif not isinstance(value, set):
                value: set[H] = set(value)
            return self.__class__(self.__inner_set - value)

    def __xor__(self, value: generic.Iterable[H], /) -> "SafeSet[H]":
        """ Return self^value. """
        if not isinstance(value, generic.Iterable):
            raise TypeError(f"value '{repr(value)}' (type={type(value)}) is not iterable")
        with self.lock(value):
            if isinstance(value, SafeSet):
                value = value.__inner_set
            elif not isinstance(value, set):
                value: set[H] = set(value)
            return self.__class__(self.__inner_set ^ value)

    # __hash__ is None because order is not guaranteed and its contents are not guaranteed to be ordered
    __hash__ = None
