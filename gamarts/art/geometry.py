"""The geometry module contains arts build from a geometry."""

from typing import Sequence, Tuple, Union
from pygame import Surface, SRCALPHA, mask as msk, Color, gfxdraw, draw
from .art import Art
from ..transform import Transformation
from pygamecv import rectangle, circle, ellipse, polygon, rounded_rectangle

RGBAOutput = Tuple[int, int, int, int]
ColorValue = Union[Color, int, str, Tuple[int, int, int], RGBAOutput, Sequence[int]]

class Rectangle(Art):
    """A Rectangle is an Art representing a rectangle."""

    def __init__(
        self,
        color: ColorValue,
        width: int,
        height: int,
        thickness: int = 0,
        transformation: Transformation = None,
    ):
        """
        A Rectangle is an Art representing a rectangle.

        Params:
        ---
        - color: ColorValue, the color of the rectangle.
        - width: int, the width of the art.
        - height: int, the height of the art. 
        - thickness: int, the thickness of the line used to draw the art.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """

        super().__init__(transformation)
        self.color = Color(color)
        self._initial_width, self.initial_height = width, height
        self._width = width
        self._height = height
        self.thickness = thickness
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        surf = Surface((self._initial_width, self.initial_height), SRCALPHA if self.color.a != 255 and self.thickness != 0 else 0)
        # Pygamecv's paradigm is: defining the control points and let the thickness go outside of the geometry
        # Here, we unsure the width and height are excatly what is asked to be, not width + thickness and height + thickness
        rect = (self.thickness//2, self.thickness//2, self._initial_width - self.thickness, self.initial_height - self.thickness)
        rectangle(surf, rect, self.color, self.thickness)
        self.surfaces = (surf,)
        self._durations = (0,)

class RoundedRectangle(Art):
    """A RoundedRectangle is an Art representing rounded rectangle."""

    def __init__(
        self,
        color: ColorValue,
        width: int,
        height: int,
        top_left: int,
        top_right: int = None,
        bottom_left: int = None,
        bottom_right: int = None,
        thickness: int = 0,
        transformation: Transformation = None,
        allow_antialias: bool = True,
        background_color: ColorValue = None
    ):
        """
        A RoundedRectangle is an Art representing rounded rectangle.

        Params:
        ---
        - color: ColorValue, the color of the rounded rectangle.
        - width: int, the width of the art.
        - height: int, the height of the art. 
        - top_left, top_right, bottom_left, bottom_right: the radii of the rounded corners.
        If one of the 3 last is None, the value for the top_left corner is used instead.
        - thickness: int, the thickness of the line used to draw the art.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        - background_color: ColorValue, the color of the background. This is used to make better renders when antialias is used.
        """
        super().__init__(transformation)
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.color = Color(color)
        self.thickness = thickness
        self._width = self._initial_width = width
        self._height = self.initial_height = height
        self.allow_antialias = allow_antialias
        self.background_color = background_color
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        surf = Surface((self._initial_width, self.initial_height), SRCALPHA)
        if self.background_color is not None: # Useful in case of antialias
            surf.fill((*self.background_color[:3], 0))
        rect = (self.thickness//2, self.thickness//2, self._initial_width - self.thickness, self.initial_height - self.thickness)
        rounded_rectangle(surf, rect, self.color, self.thickness, ld_kwargs.get("antialias", False) and self.allow_antialias,
                          self.top_left, self.top_right, self.bottom_left, self.bottom_right)
        self._surfaces = (surf,)
        self._durations = (0,)

class Circle(Art):
    """A Circle is an Art representing a circle."""

    def __init__(
        self,
        color: ColorValue,
        radius: int,
        thickness: int = 0,
        transformation: Transformation = None,
        allow_antialias: bool = True,
        background_color: Color = None
    ):
        """
        A Circle is an Art representing a circle.

        Params:
        ---
        - color: ColorValue, the color of the circle.
        - radius: int, the radius of circle. The art will have a width and height of twice the radius.
        - thickness: int, the thickness of the line used to draw the art.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        - background_color: ColorValue, the color of the background. This is used to make better renders when antialias is used.
        """
        super().__init__(transformation)
        self.radius = radius
        self.color = Color(color)
        self.thickness = thickness
        self._height = 2*radius
        self._width = 2*radius
        self.allow_antialias = allow_antialias
        self.background_color = background_color
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        surf = Surface((self.radius*2, self.radius*2), SRCALPHA)
        if self.background_color is not None: # Useful in case of antialias
            surf.fill((*self.background_color[:3], 0))
        radius = self.radius - self.thickness//2
        if radius > 0:
            circle(surf, (self.radius, self.radius), radius, self.color,
                self.thickness, ld_kwargs.get("antialias", False) and self.allow_antialias)
        else:
            circle(surf, (self.radius, self.radius), self.radius, self.color,
                0, ld_kwargs.get("antialias", False) and self.allow_antialias)

        self._surfaces = (surf,)
        self._durations = (0,)

class Ellipse(Art):
    """An Ellipse is an Art with a colored ellipse at the center."""

    def __init__(
        self,
        color: Color,
        radius_x: int,
        radius_y: int,
        thickness: int = 0,
        transformation: Transformation = None,
        allow_antialias: bool = True,
        background_color: Color = None
    ) -> None:
        """
        An Ellipse is an Art representing a ellipse.

        Params:
        ---
        - color: ColorValue, the color of the the ellipse.
        - radius_x: int, the horizontal radius of the ellipse. The width of the art is of twice this value. 
        - radius_y: int, the vertical radius of the ellipse. The height of the art is of twice this value. 
        - thickness: int, the thickness of the line used to draw the art.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        - background_color: ColorValue, the color of the background. This is used to make better renders when antialias is used.
        """
        self.color = color
        self.thickness = thickness
        super().__init__(transformation)
        self.radius_x, self.radius_y = radius_x, radius_y
        self._height = radius_y*2
        self._width = radius_x*2
        self.allow_antialias = allow_antialias
        self.background_color = background_color
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        surf = Surface((self.radius_x*2, self.radius_y*2), SRCALPHA)
        if self.background_color is not None: # Useful in case of antialias
            surf.fill((*self.background_color[:3], 0))
        radius_x = self.radius_x - self.thickness //2
        radius_y = self.radius_y - self.thickness //2
        if radius_x > 0 and radius_y > 0:
            ellipse(surf, (self.radius_x, self.radius_y), radius_x, radius_y, self.color, self.thickness, ld_kwargs.get("antialias", False) and self.allow_antialias, 0)
        else:
            ellipse(surf, (self.radius_x, self.radius_y), self.radius_x, self.radius_y, self.color, 0, ld_kwargs.get("antialias", False) and self.allow_antialias, 0)
        self._surfaces = (surf,)
        self._durations = (0,)

class Polygon(Art):
    """A Polygon is an Art representing a polygon."""

    def __init__(
        self,
        color: Color,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        transformation: Transformation = None,
        allow_antialias: bool = True,
        background_color: Color = None
    ):      
        """
        A Circle is an Art representing a polygon.

        Params:
        ---
        - color: ColorValue, the color of the polygon.
        - points: Sequence[tuple[int, int]], the points used to draw the polygon. All points will be translated in the plan so that
        min(p[0] for p in points) == min(p[1] for p in points) == 0. The width and height of the art are equal to
        max(p[0] for p in points) and max(p[1] for p in points) after the translation.
        - thickness: int, the thickness of the line used to draw the art.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        - background_color: ColorValue, the color of the background. This is used to make better renders when antialias is used.
        """

        self.points = points
        self.thickness = thickness
        self.color = color
        super().__init__(transformation)

        min_x = min(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)

        self.points = [(p[0] - min_x + thickness//2, p[1] - min_y + thickness//2) for p in points]

        self._height = self._initial_height = max(p[1] for p in self.points) + thickness//2
        self._width = self._initial_width = max(p[0] for p in self.points) + thickness//2
        self.allow_antialias = allow_antialias
        self.background_color = background_color
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):

        surf = Surface((self._initial_width, self._initial_height), SRCALPHA)
        if self.background_color is not None:
            surf.fill((*self.background_color[:3], 0))
        polygon(surf, self.points, self.color, self.thickness, ld_kwargs.get("antialias", False) and self.allow_antialias)

        self._surfaces = (surf,)
        self._durations = (0,)

class TexturedPolygon(Art):
    """A Textured polygon represents a polygon filled with an art.."""

    def __init__(
        self,
        texture: Art,
        points: Sequence[tuple[int, int]],
        transformation: Transformation = None,
    ):
        """
        A Textured polygon represents a polygon filled with an art.
        
        Params:
        ----
        - texture: Art, the Art drawn inside the polygon. The TexturedPolygon will have the same width, height, durations and introduction
        as its texture. The surfaces use to create the TexturedPolygon are the surfaces of the texture when the TexturedPolygon is loaded.
        - points: Sequence[tuple[int, int]] the list of points used to draw the polygon.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """


        self.points = points
        super().__init__(transformation)
        self._height = max(p[1] for p in self.points)
        self._width = max(p[0] for p in self.points)
        self._find_initial_dimension()
        self.texture = texture

    def _load(self, **ld_kwargs):

        surfaces = []
        need_to_unload = False

        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load(**ld_kwargs)

        else: # the texture might have change, so can its dimensions.
            self._width = self.texture.width
            self._height = self.texture.height
            self._find_initial_dimension()

        for surf in self.texture.surfaces:
            background = Surface((self._width, self._height), SRCALPHA)
            gfxdraw.textured_polygon(background, self.points, surf.convert_alpha(), 0, 0)
            surfaces.append(background)

        self._surfaces = tuple(surfaces)
        self._durations = self.texture.durations
        self._introduction = self.texture.introduction

        if need_to_unload:
            self.texture.unload()

class TexturedCircle(Art):
    """A TexturedCircle is an Art with a textured circle at the center of it."""

    def __init__(
        self,
        texture: Art,
        radius: int,
        center: tuple[int, int] = None,
        draw_top_right: bool = True,
        draw_top_left: bool = True,
        draw_bottom_left: bool = True,
        draw_bottom_right: bool = True,
        transformation: Transformation = None,
    ):
        """
        A TexturedCircle represents a circle filled with an art.
        
        Params:
        ----
        - texture: Art, the Art drawn inside the polygon. The TexturedPolygon will have the same width, height, durations and introduction
        as its texture. The surfaces use to create the TexturedPolygon are the surfaces of the texture when the TexturedPolygon is loaded.
        - radius: the radius of the circle
        - center: the center of the circle. By default, the center of the Art. The circle may not be fully drawn.
        - draw_top_right, draw_top_left, draw_bottom_left, draw_bottom_right: bool, specify whether the corresponding quart should be drawn.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """

        super().__init__(transformation)
        self.radius = radius
        self.draw_top_right = draw_top_right
        self.draw_top_left = draw_top_left
        self.draw_bottom_left = draw_bottom_left
        self.draw_bottom_right = draw_bottom_right
        if center is None:
            center = texture.width//2, texture.height//2
        self.center = center
        self._width = texture.width
        self._height = texture.height
        self.texture = texture
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load(**ld_kwargs)
    
        else: # the texture might have change, so can its dimensions.
            self._width = self.texture.width
            self._height = self.texture.height
            self._find_initial_dimension()

        surf = Surface((self._width, self._height), SRCALPHA)
        draw.circle(surf, (255, 255, 255, 255), self.center,
            self.radius, 0, self.draw_top_right, self.draw_top_left, self.draw_bottom_left, self.draw_bottom_right)
        mask = msk.from_surface(surf, 127)
        self._surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self._durations = self.texture.durations
        self._introduction = self.texture.introduction


        if need_to_unload:
            self.texture.unload()

class TexturedEllipse(Art):
    """A TexturedEllipse represents an ellipse filled with an art."""

    def __init__(
        self,
        texture: Art,
        radius_x: int,
        radius_y: int,
        center: tuple[int, int] = None,
        transformation: Transformation = None,
    ) -> None:   
        """
        A TexturedEllipse represents an ellipse filled with an art.
        
        Params:
        ----
        - texture: Art, the Art drawn inside the polygon. The TexturedPolygon will have the same width, height, durations and introduction
        as its texture. The surfaces use to create the TexturedPolygon are the surfaces of the texture when the TexturedPolygon is loaded.
        - radius_x, radius_y: int, the horizontal and vertical radii of the ellipse.
        - center: tuple[int, int], default is the center of the art. The center of the ellipse.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """
        super().__init__(transformation)
        if center is None:
            center = texture.width//2, texture.height//2
        self.center = center
        self.rect = (self.center[0] - radius_x, self.center[0] - radius_y, radius_x*2, radius_y*2)
        self._width = texture.width
        self._height = texture.height
        self.texture = texture
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load(**ld_kwargs)
        
        else: # the texture might have change, so can its dimensions.
            self._width = self.texture.width
            self._height = self.texture.height
            self._find_initial_dimension()

        surf = Surface((self._width, self._height), SRCALPHA)
        draw.ellipse(surf, (255, 255, 255, 255), self.rect, 0)
        mask = msk.from_surface(surf, 127)
        self._surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self._durations = self.texture.durations
        self._introduction = self.texture.introduction

        if need_to_unload:
            self.texture.unload()

class TexturedRoundedRectangle(Art):
    """A TexturedRoundedRectangle is an Art with rounded corners."""

    def __init__(
        self,
        texture: Art,
        top_left: int,
        top_right: int = None,
        bottom_left: int = None,
        bottom_right: int = None,
        transformation: Transformation = None,
    ):
        """
        A TexturedRoundedRectangle is an Art with rounded corners.
        
        Params:
        ----
        - texture: Art, the Art drawn inside the polygon. The TexturedPolygon will have the same width, height, durations and introduction
        as its texture. The surfaces use to create the TexturedPolygon are the surfaces of the texture when the TexturedPolygon is loaded.
        - top_left, top_right, bottom_left, bottom_right: int. The radii of the corners. If any of the 3 last is None, it it repplaced by the
        value for top_left.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """

        super().__init__(transformation)
        self.top_left = top_left
        self.top_right = top_right if not top_right is None else top_left
        self.bottom_left = bottom_left if not bottom_left is None else top_left
        self.bottom_right = bottom_right if not bottom_right is None else top_left
        self._height = texture.height
        self._width = texture.width
        self.texture = texture

        self._find_initial_dimension()

    def _load(self, **ld_kwargs):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load(**ld_kwargs)

        surf = Surface((self.width, self.height), SRCALPHA)
        draw.rect(
            surf,
            (255, 255, 255, 255),
            (0, 0, self.width, self.height),
            0,
            -1,
            self.top_left,
            self.top_right,
            self.bottom_left,
            self.bottom_right
        )
        mask = msk.from_surface(surf, 127)
        self._surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self._durations = self.texture.durations
        self._introduction = self.texture.introduction

        if need_to_unload:
            self.texture.unload()
