"""The commone module contains the LoadingError Exception and some common objects."""
from typing import Union, Tuple, Sequence
from pygame import Color


class LoadingError(Exception):
    """Error to be raised when an error related to the loading of an Art occurs."""

ColorValue = Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]]
