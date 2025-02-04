from ._combination import Blit, Average, Concatenate
from ._transformation import (
    Transformation, Pipeline,
    SetIntroductionIndex, SetIntroductionTime, SlowDown, SpeedUp, ResetDuration, ResetDurations,
    Resize, Rotate, Crop, VerticalChop, HorizontalChop, Last, ExtractMany, ExtractOne, First, Flip, Transpose,
    Zoom, Pad
)
from ._drawing import DrawArc, DrawCircle, DrawEllipse, DrawLine, DrawLines, DrawPie, DrawPolygon, DrawRectangle, DrawRoundedRectantle
from ._effect import Saturate, Darken, Lighten, Desaturate, SetAlpha, ShiftHue, Gamma, GrayScale, AdjustContrast, RBGMap, RGBAMap, Invert, AddBrightness
