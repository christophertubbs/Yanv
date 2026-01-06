"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import inspect
import typing
import re

import collections.abc as generic

import numpy
import pydantic
import xarray

from yanv.utilities.netcdf import get_random_values
from yanv.model.dimension import Dimension

STRING_PATTERN = re.compile(r"S\d+$")


def make_value_serializable(value: typing.Any, encountered_items: list[typing.Any] = None):
    if isinstance(value, (numpy.floating, float)) and numpy.isnan(value):
        return "NaN"

    if isinstance(value, numpy.number):
        return value.item()

    if isinstance(value, numpy.bool):
        return bool(value)

    if isinstance(value, (int, str, float, bool)):
        return value

    if encountered_items is None:
        encountered_items = []

    try:
        if not isinstance(value, numpy.ndarray) and value in encountered_items:
            return None
    except ValueError as e:
        raise ValueError(f"Could not check to see if '{value}' (type={type(value)}) has been encountered in a {type(encountered_items)}: {e}") from e

    if not isinstance(value, numpy.ndarray):
        encountered_items.append(value)

    if isinstance(value, bytes):
        return value.decode()

    if hasattr(value, 'name'):
        if inspect.isroutine(value.name):
            value = value.name()
            make_value_serializable(value, encountered_items=encountered_items)
        elif isinstance(value.name, str):
            return value.name

    if isinstance(value, numpy.ndarray):
        value = value.tolist()
    elif hasattr(value, "item") and inspect.isroutine(value.item):
        value = value.item()
        return make_value_serializable(value, encountered_items=encountered_items)

    if isinstance(value, generic.Mapping):
        return {
            key.decode() if isinstance(key, bytes) else str(key): make_value_serializable(value=val, encountered_items=encountered_items)
            for key, val in value.items()
        }
    if isinstance(value, generic.Iterable) and not isinstance(value, (str, bytes)):
        return [
            make_value_serializable(value=item, encountered_items=encountered_items)
            for item in value
        ]
    return str(value)


class Variable(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> typing.Sequence[Variable]:
        dimensions = {
            dim.name: dim
            for dim in Dimension.from_xarray(dataset)
        }

        variables: typing.List[Variable] = list()

        for variable_name in dataset.variables.keys():
            variable = dataset[variable_name]

            # NOTE: Separating random sampling into a separate call since this can be wildly expensive
            #random_values = get_random_values(variable=variable, size=5)

            #if random_values is not None:
            #    examples = [str(value) for value in random_values]
            #else:
            #    examples = []

            kwargs = dict(
                name=variable_name,
                datatype=str(variable.dtype),
                count=variable.size,
                attributes={
                    key: make_value_serializable(value)
                    for key, value in variable.attrs.items()
                },
                encoding={
                    key: make_value_serializable(value)
                    for key, value in variable.encoding.items()
                },
                dimensions=[
                    dimensions[name]
                    for name in variable.dims
                ]
            )

            if variable.shape == (1, ):
                kwargs['value'] = str(variable.values[0])

            if 'long_name' in variable.attrs.keys():
                kwargs['long_name'] = variable.attrs['long_name']

            if 'units' in variable.attrs.keys():
                kwargs['units'] = variable.attrs['units']
            elif 'units' in variable.encoding.keys():
                kwargs['units'] = variable.encoding['units']

            variables.append(
                cls(**kwargs)
            )

        return variables

    name: str
    datatype: str
    count: int
    dimensions: typing.List[Dimension] = pydantic.Field(default_factory=list)
    examples: typing.List[str] = pydantic.Field(default_factory=list)
    long_name: typing.Optional[str] = pydantic.Field(default=None)
    units: typing.Optional[str] = pydantic.Field(default=None)
    attributes: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default_factory=dict)
    encoding: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default_factory=dict)
    value: typing.Optional[typing.Any] = pydantic.Field(default=None)

    def is_string(self) -> bool:
        return STRING_PATTERN.search(self.datatype.strip()) is not None

    def __str__(self):
        representation = f"{'string' if self.is_string() else self.datatype} "
        representation += self.long_name if self.long_name else self.name

        if self.dimensions:
            representation += f"({', '.join([str(dimension) for dimension in self.dimensions])})"

        if self.units:
            representation += f" => {self.units}"

        return representation

    def __getitem__(self, key: str) -> typing.Any:
        return self.attributes[key]

    def __repr__(self):
        return self.__str__()
