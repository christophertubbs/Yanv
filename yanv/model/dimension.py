"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic
import xarray


class Dimension(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> typing.Sequence[Dimension]:
        dimensions: typing.List[Dimension] = list()

        for dimension_name, count in dataset.dims.items():
            variable: xarray.Variable = dataset.variables[dimension_name]
            dimensions.append(
                Dimension(
                    name=dimension_name,
                    count=count,
                    datatype=str(variable.dtype),
                    attributes={
                        key: value
                        for key, value in variable.attrs.items()
                    }
                )
            )

        return dimensions

    name: str
    count: int
    datatype: str
    attributes: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default_factory=dict)