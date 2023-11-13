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


def get_random_variable_coordinate(variable: xarray.Variable) -> typing.Sequence[int]:
    coordinates = []

    needed_dimensions = [variable.dims[index] for index in range(len(variable.dims) - 1)]

    for dimension in needed_dimensions:
        coordinates.append(random.randint(0, variable[dimension].size))

    return coordinates


def get_random_values(
    variable: typing.Union[xarray.Variable, xarray.DataArray],
    size: int = None
) -> typing.Optional[typing.Sequence]:
    if size is None:
        size = 1

    random_values: typing.List[_VALUE_TYPE] = []

    dimension_count = len(variable.dims)

    if dimension_count == 0:
        return None
    elif dimension_count == 1:
        return choice(variable.values, size=size)

    max_attempts = 5
    outer_attempts = 0

    while len(random_values) < size and outer_attempts < max_attempts:
        attempts = 0
        coordinates = None

        while attempts < max_attempts:
            coordinates = get_random_variable_coordinate(variable=variable)
            attempts += 1

        if coordinates is None:
            break

        attempts = 0

        while attempts < max_attempts:
            sample_array = variable.values

            for coordinate in coordinates:
                sample_array = sample_array[coordinate]

            random_value = choice(sample_array)

            if not numpy.isnan(random_value) and random_value not in random_values:
                random_values.append(random_value)
                break

            attempts += 1

        outer_attempts += 1

    return random_values
