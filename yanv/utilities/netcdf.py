"""
Utilities used to help manipulate netcdf data
"""
from __future__ import annotations

import random
import typing
from datetime import datetime

import numpy
import xarray
from numpy import datetime64

from numpy.random import choice
from pandas import Timestamp
from xarray.core.coordinates import DataArrayCoordinates

_VALUE_TYPE = typing.TypeVar("_VALUE_TYPE")


def variable_is_spatial(variable: xarray.DataArray) -> bool:
    """
    Determines if a given variable represents spatial data

    :param variable: The variable to check
    :return: Whether the data represented by the variable is spatial
    """
    variable_coordinates: DataArrayCoordinates = variable.coords

    if len(variable_coordinates.dims) < 2:
        return False

    y_dimension, x_dimension = variable_coordinates.dims[-2:]

    if y_dimension not in variable_coordinates.variables or x_dimension not in variable_coordinates.variables:
        return False

    x_variable = variable_coordinates.variables[x_dimension]
    y_variable = variable_coordinates.variables[y_dimension]

    axis_attribute = '_CoordinateAxisType'

    return axis_attribute in x_variable.attrs and axis_attribute in y_variable.attrs


def variable_is_temporal(variable: xarray.DataArray) -> bool:
    coordinates = variable.coords

    for coordinate_name in reversed(coordinates.dims):
        coordinate_variable = coordinates.variables.get(coordinate_name)

        if coordinate_variable is None:
            continue

        coordinate_type = coordinate_variable.dtype.type

        # This variable is considered temporal if its type is a datetime type and it has more than one value
        #   A datetime variable isn't considered temporal if it only has 1 value since it doesn't describe data at
        #   more than one time
        if issubclass(coordinate_type, (datetime64, datetime, Timestamp)) and coordinate_variable.size > 1:
            return True

    return False


def get_random_values(
    variable: xarray.DataArray,
    size: int = None
) -> typing.Optional[typing.Sequence]:
    """
    Retrieve a random sample of values from a variable

    :param name: The name of the variable
    :param variable: The variable to sample
    :param size: The requested amount of values to retrieve
    :return: A sequence of values from the variable
    """
    if size is None:
        size = 1

    max_attempts = 25

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

        while attempts < max_attempts:
            variable_coordinates = {
                key: random.randint(0, size - 1)
                for key, size in variable.coords.sizes.items()
                if key != variable.coords.dims[-1]
            }

            sample_array = variable.isel(variable_coordinates)

            random_sample = choice(sample_array, size=min(size, sample_array.size))

            for random_value in random_sample:
                if not numpy.isnan(random_value) and random_value not in random_values:
                    random_values.append(random_value)
                if len(random_values) >= size:
                    return random_values

            attempts += 1

        outer_attempts += 1

    return random_values
