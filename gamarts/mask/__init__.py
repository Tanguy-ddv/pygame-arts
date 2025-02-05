"""
The mask module contains masks. Masks are objects used to select part of an image on which apply an effect.
There are 6 types of Masks:
The first type is composed of only one class: MatrixMask
The second one is composed of binary geometrical masks: Circle, Ellipsis, Rectangle etc.
The third one is composed of gradient geometrical masks: GradientCircle, GradientRectangle etc.
The fourth one is composed of masks extracted from arts or from images.
The fifth one is combinations or transformation of other masks.
The last one is moving masks.
"""
from .mask import Mask, MatrixMask, FreeMask, Circle, Ellipse, GradientCircle, GradientRectangle, Rectangle, RoundedRectangle, Polygon
from .moving_mask import (
    WrappingMovingCircle, WrappingMovingEllipse, WrappingMovingGradientCircle, WrappingMovingGradientRectangle, WrappingMovingRectangle, WrappingMovingRoundedRectangle,
    BouncingMovingCircle, BouncingMovingEllipse, BouncingMovingGradientCircle, BouncingMovingGradientRectangle, BouncingMovingRectangle, BouncingMovingRoundedRectangle,
    DisappearingMovingCircle, DisappearingMovingEllipse, DisappearingMovingGradientCircle, DisappearingMovingGradientRectangle, DisappearingMovingRectangle, DisappearingMovingRoundedRectangle
)

from .transformation import FromArtAlpha, FromArtColor, FromImageColor, SumOfMasks, ProductOfMasks, AverageOfMasks, BinaryMask, BlitMaskOnMask, InvertedMask, TransformedMask

