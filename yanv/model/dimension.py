"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import inspect
import typing

import numpy
import pydantic
import xarray


def make_value_serializable(value: typing.Any):
    if isinstance(value, numpy.ndarray):
        value = value.tolist()
    elif hasattr(value, "item") and inspect.isroutine(value.item):
        value = value.item()
    return value


class Dimension(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> typing.Sequence[Dimension]:
        dimensions: typing.List[Dimension] = list()

        for dimension_name, count in dataset.dims.items():
            variable: xarray.Variable = dataset.variables[dimension_name]

            kwargs = {
                "name": dimension_name,
                "count": count,
                "datatype": str(variable.dtype),
                "minimum": str(variable.values.min()),
                "maximum": str(variable.values.max()),
                "attributes": {
                    key: make_value_serializable(value)
                    for key, value in variable.attrs.items()
                }
            }

            if "long_name" in variable.attrs.keys():
                kwargs['long_name'] = variable.attrs['long_name']

            dimensions.append(
                Dimension(**kwargs)
            )

        return dimensions

    name: str
    count: int
    datatype: str
    minimum: str
    maximum: str
    long_name: typing.Optional[str] = pydantic.Field(default=None)
    attributes: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default_factory=dict)

    def __len__(self):
        return self.count

    def __str__(self):
        return f"{self.datatype} {self.name}({self.count})"

    def __repr__(self):
        return self.__str__()