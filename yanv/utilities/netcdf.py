"""
Utilities used to help manipulate netcdf data
"""
from __future__ import annotations

import random
import typing

import numpy
import xarray

from numpy.random import choice


_VALUE_TYPE = typing.TypeVar("_VALUE_TYPE")


def get_random_variable_coordinate(name: str, variable: xarray.Variable) -> typing.Sequence[int]:
    coordinates = []

    needed_dimensions = [variable.dims[index] for index in range(len(variable.dims) - 1)]

    for dimension in needed_dimensions:
        try:
            coordinates.append(random.randint(0, variable.sizes[dimension] - 1))
        except BaseException as index_exception:
            message = f"Could not index {name} on dimension '{dimension}' " \
                      f"with the required dimensions '{needed_dimensions}' because {str(index_exception)}"
            raise IndexError(message)

    return coordinates


def get_random_values(
    name: str,
    variable: typing.Union[xarray.Variable, xarray.DataArray],
    size: int = None
) -> typing.Optional[typing.Sequence]:
    if size is None:
        size = 1

    max_attempts = 5

    random_values: typing.List[_VALUE_TYPE] = []

    dimension_count = len(variable.dims)

    if dimension_count == 0:
        return None
    elif dimension_count == 1:
        values = set(choice(variable.values, size=size))
        attempts = 0
        while len(values) < size and attempts < max_attempts:
            new_choices = choice(variable.values, size=size)

            for new_value in new_choices:
                if new_value is not None and not numpy.isnan(new_value):
                    values.add(new_value)
                if len(values) >= size:
                    return [value for value in values]
            attempts += 1
        return [value for value in values]

    outer_attempts = 0

    while len(random_values) < size and outer_attempts < max_attempts:
        attempts = 0
        coordinates = None

        while attempts < max_attempts:
            coordinates = get_random_variable_coordinate(name=name, variable=variable)
            attempts += 1

        if coordinates is None:
            break

        attempts = 0

        while attempts < max_attempts:
            sample_array = variable.values

            applied_coordinates = []
            for coordinate in coordinates:
                try:
                    applied_coordinates.append(coordinate)
                    sample_array = sample_array[coordinate]
                except BaseException as coordinate_exception:
                    message = f"Failed to index '{name}' at the coordinate " \
                              f"'[{', '.join([str(index) for index in applied_coordinates])}]' with a total expected " \
                              f"coordinate of `[{', '.join([str(index) for index in coordinates])}]`"
                    raise Exception(message) from coordinate_exception

            random_value = choice(sample_array)

            if not numpy.isnan(random_value) and random_value not in random_values:
                random_values.append(random_value)
                break

            attempts += 1

        outer_attempts += 1

    return random_values
