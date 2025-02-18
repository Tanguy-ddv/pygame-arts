"""
gamarts is a python library used to represent animations and static images with the same Art class.
It also introduce clever loading and unloading methods.
"""
from gamarts.art import (
    GIFFile, ImageFile, ImageFolder, Rectangle, RoundedRectangle, Circle, Ellipse, Polygon,
    TexturedCircle, TexturedEllipse, TexturedPolygon, TexturedRoundedRectangle, Art
)
import gamarts.mask as mask
import gamarts.transform as transform

LD_KWARGS = {'antialias': False, 'cost_threshold': 200_000}
