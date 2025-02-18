"""The convert module contains transformations related to a conversion format."""
from pygame import transform as tf, Surface
from .transformation import Transformation

class GrayScale(Transformation):
    """
    The gray scale transformation turns the art into a black and white art. The frames are converted in a 8-bits-per-pixel format.
    """

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        graysurfeaces = tuple(tf.grayscale(surf) for surf in surfaces)
        return graysurfeaces, durations, introduction, None, width, height

class ConvertRGBA(Transformation):
    """The convert RGBA tranformation adds an alpha layer to the art. The frames are converted in a 32-bits-per-pixel format."""

    def apply(self, surfaces, durations, introduction, index, width, height, **ld_kwargs):
        surfaces = tuple(surf.convert_alpha() for surf in surfaces)
        return surfaces, durations, introduction, None, width, height

class ConvertRGB(Transformation):
    """The convert RGB transformation converts the frames in a 24-bits-per-pixel format. The alpha layer is removed."""
    def apply(self, surfaces, durations, introduction, index, width, height, **ld_kwargs):
        surfaces = tuple(surf.convert() for surf in surfaces)
        return surfaces, durations, introduction, None, width, height
