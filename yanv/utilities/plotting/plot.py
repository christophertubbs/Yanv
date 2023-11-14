"""
@TODO: Put a module wide description here
"""
from __future__ import annotations

import typing

import xarray

from messages.requests.data import PlotDataRequest


class TooManyGroupsException(Exception):
    ...


def plot_data(request: PlotDataRequest, data: xarray.Dataset, animate: bool = None) -> str:
    if animate in (True, None) and request.should_animate():
        return plot_animation(request=request, data=data)


def plot_animation(request: PlotDataRequest, data: xarray.Dataset) -> str:
    pass