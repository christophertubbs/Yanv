"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import inspect
import random
import typing
import re

import numpy
import pydantic
import xarray

from numpy.random import choice

from utilities.netcdf import get_random_values
from yanv.model.dimension import Dimension

STRING_PATTERN = re.compile(r"S\d+$")


def make_value_serializable(value: typing.Any):
    if isinstance(value, numpy.ndarray):
        value = value.tolist()
    elif hasattr(value, "item") and inspect.isroutine(value.item):
        value = value.item()
    return value


class Variable(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> typing.Sequence[Variable]:
        dimensions = {
            dim.name: dim
            for dim in Dimension.from_xarray(dataset)
        }

        variables: typing.List[Variable] = list()

        for variable_name, variable in dataset.variables.items():
            random_values = get_random_values(name=str(variable_name), variable=variable, size=5)

            if random_values is not None:
                examples = [str(value) for value in random_values]
            else:
                examples = []

            kwargs = dict(
                name=variable_name,
                datatype=str(variable.dtype),
                count=variable.size,
                attributes={
                    key: make_value_serializable(value)
                    for key, value in variable.attrs.items()
                },
                dimensions=[
                    dimensions[name]
                    for name in variable.dims
                ],
                examples=examples
            )

            if 'long_name' in variable.attrs.keys():
                kwargs['long_name'] = variable.attrs['long_name']

            if 'units' in variable.attrs.keys():
                kwargs['units'] = variable.attrs['units']

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