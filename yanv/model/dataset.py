"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import inspect
import os
import pathlib
import typing

import numpy
import pydantic
import xarray
from pydantic import field_serializer
from pydantic import model_serializer
from pydantic import model_validator

from yanv.model.dimension import Dimension
from yanv.model.variable import Variable


def make_value_serializable(value: typing.Any):
    if isinstance(value, numpy.ndarray):
        value = value.tolist()
    elif hasattr(value, "item") and inspect.isroutine(value.item):
        value = value.item()
    return value


class Dataset(pydantic.BaseModel):
    @classmethod
    def from_xarray(cls, dataset: xarray.Dataset, name: str = None) -> Dataset:
        variables = Variable.from_xarray(dataset)
        dimensions = Dimension.from_xarray(dataset)
        attributes = {
            key: make_value_serializable(value)
            for key, value in dataset.attrs.items()
        }
        source = dataset.encoding.get("source")

        kwargs = dict(
            variables=variables,
            dimensions=dimensions,
            attributes=attributes,
            sources=[source]
        )

        if name:
            kwargs['name'] = name

        return cls(**kwargs)

    variables: typing.List[Variable] = pydantic.Field(default_factory=list)
    dimensions: typing.List[Dimension] = pydantic.Field(default_factory=list)
    attributes: typing.Dict[str, typing.Any] = pydantic.Field(default_factory=dict)
    sources: typing.List[os.PathLike] = pydantic.Field(default_factory=list)
    name: typing.Optional[str] = pydantic.Field(default=None)

    @field_serializer("sources")
    def serialize_sources(self, sources, _info):
        return [str(source) for source in sources]

    @model_validator(mode="after")
    def determine_name(self) -> Dataset:
        if self.name:
            return self

        if len(self.sources) == 1:
            self.name = str(self.sources[0])
        elif len(self.sources) > 1:
            endings = [str(pathlib.Path(source).name) for source in self.sources]
            self.name = ' + '.join(endings)
        else:
            self.name = "Unnamed"

        return self

    @property
    def variable_names(self) -> typing.Sequence[str]:
        return [
            variable.name
            for variable in self.variables
        ]

    @property
    def dimension_names(self) -> typing.Sequence[str]:
        return [
            dimension.name
            for dimension in self.dimensions
        ]

    def get_dimension(self, name: str) -> Dimension:
        possible_dimensions = [
            dimension
            for dimension in self.dimensions
            if dimension.name == name
        ]

        if not possible_dimensions:
            possible_dimensions = [
                dimension
                for dimension in self.dimensions
                if dimension.name.lower() == name.lower()
            ]

        if not possible_dimensions:
            raise KeyError(f"There are no dimensions named '{name}'")

        return possible_dimensions[0]

    def get_variable(self, name: str) -> Variable:
        possible_variables = [
            variable
            for variable in self.variables
            if variable.name == name
        ]

        if not possible_variables:
            possible_variables = [
                variable
                for variable in self.variables
                if variable.name.lower() == name.lower()
            ]

        if not possible_variables:
            raise KeyError(f"There are no variables named '{name}'")

        return possible_variables[0]

    def __getitem__(self, key: str) -> typing.Any:
        if key in self.variable_names:
            return self.get_variable(key)

        return self.attributes[key]

    def __str__(self):
        return f"Dataset: {', '.join([str(variable) for variable in self.variables])}"

    def __repr__(self):
        return self.__str__()