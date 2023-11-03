"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import pydantic
import xarray

from yanv.model.dimension import Dimension
from yanv.model.variable import Variable


class Dataset(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset) -> Dataset:
        variables = Variable.from_xarray(dataset)
        dimensions = Dimension.from_xarray(dataset)
        attributes = {
            key: value
            for key, value in dataset.attrs.items()
        }
        source = dataset.encoding.get("source")

        return cls(
            variables=variables,
            dimensions=dimensions,
            attributes=attributes,
            source=source
        )

    variables: typing.List[Variable] = pydantic.Field(default_factory=list)
    dimensions: typing.List[Dimension] = pydantic.Field(default_factory=list)
    attributes: typing.Dict[str, typing.Any]
    source: str