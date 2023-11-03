"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic
import xarray

from yanv.model.dimension import Dimension


class Variable(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> typing.Sequence[Variable]:
        dimensions = {
            dim.name: dim
            for dim in Dimension.from_xarray(dataset)
        }

        variables: typing.List[Variable] = list()

        for variable_name, variable in dataset.data_vars.items():
            variables.append(
                cls(
                    name=variable_name,
                    datatype=str(variable.dtype),
                    attributes={
                        key: value
                        for key, value in variable.attrs.items()
                    },
                    dimensions=[
                        dimensions[name]
                        for name in variable.dims
                    ]
                )
            )

        return variables

    name: str
    datatype: str
    attributes: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default_factory=dict)
    dimensions: typing.List[Dimension] = pydantic.Field(default_factory=list)