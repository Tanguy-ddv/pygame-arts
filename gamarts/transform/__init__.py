"""The transform module contiains all the transformations that can be applied to an Art."""
from .combination import Blit, Average, Concatenate
from .transformation import (
    Transformation, Pipeline,
    SetIntroductionIndex, SetIntroductionTime, SlowDown, SpeedUp, SetDurations,
    Resize, Rotate, Crop, VerticalChop, HorizontalChop, Last, ExtractSlice, ExtractOne, First, Flip, Transpose,
    Zoom, Pad, ExtractTime, ExtractWindow
)
from .drawing import DrawArc, DrawCircle, DrawEllipse, DrawLine, DrawLines, DrawPie, DrawPolygon, DrawRectangle, DrawRoundedRectangle
from .effect import Saturate, Darken, Lighten, Desaturate, SetAlpha, ShiftHue, Gamma, AdjustContrast, RBGMap, RGBAMap, Invert, AddBrightness
from .convert import GrayScale, ConvertRGB, ConvertRGBA
