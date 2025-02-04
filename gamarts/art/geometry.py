"""The geometry module contains arts build from a geometry."""

from typing import Sequence
from pygame import Surface, SRCALPHA, mask as msk, Color, gfxdraw, draw
from .art import Art
from ..transform import Transformation
from pygamecv import rectangle, circle, ellipse, polygon, rounded_rectangle

class Rectangle(Art):
    """A Rectangle is an Art with only one color."""

    def __init__(
        self,
        color: Color,
        width: int,
        height: int,
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
    ):
        super().__init__(transformation, force_load_on_start, permanent)

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
        self.durations = (0,)

class RoundedRectangle(Art):
    """A RoundedRectangle is an Art with a rounded rectangle inside."""

    def __init__(
        self,
        color: Color,
        width: int,
        height: int,
        top_left: int,
        top_right: int = None,
        bottom_left: int = None,
        bottom_right: int = None,
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
        allow_antialias: bool = True,
        background_color: Color = None
    ):
        super().__init__(transformation, force_load_on_start, permanent)
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.color = color
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
        self.surfaces = (surf,)
        self.durations = (0,)

class Circle(Art):
    """A Circle is an Art with a colored circle at the center of it."""

    def __init__(
        self,
        color: Color,
        radius: int,
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
        allow_antialias: bool = True,
        background_color: Color = None
    ):
        super().__init__(transformation, force_load_on_start, permanent)
        self.radius = radius
        self.color = color
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

        self.surfaces = (surf,)
        self.durations = (0,)

class Ellipse(Art):
    """An Ellipse is an Art with a colored ellipse at the center."""

    def __init__(
        self,
        color: Color,
        horizontal_radius: int,
        vertical_radius: int,
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
        allow_antialias: bool = True,
        background_color: Color = None
    ) -> None:
        self.color = color
        self.thickness = thickness
        super().__init__(transformation, force_load_on_start, permanent)
        self.radius_x, self.radius_y = horizontal_radius, vertical_radius
        self._height = vertical_radius*2
        self._width = horizontal_radius*2
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
        self.surfaces = (surf,)
        self.durations = (0,)

class Polygon(Art):
    """A Polygon is an Art with a colored polygon at the center."""

    def __init__(
        self,
        color: Color,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
        allow_antialias: bool = True,
        background_color: Color = None
    ):

        self.points = points
        self.thickness = thickness
        self.color = color
        super().__init__(transformation, force_load_on_start, permanent)

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

        self.surfaces = (surf,)
        self.durations = (0,)

class TexturedPolygon(Art):
    """A Textured polygon is a polygon filled with an art as texture."""

    def __init__(
        self,
        points: Sequence[tuple[int, int]],
        texture: Art,
        texture_top_left: tuple[int, int] = (0, 0),
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
    ):
        # for p in points:
        #     if p[0] < 0 or p[1] < 0:
        #         raise ValueError(f"All points coordinates of a polygon must have a positive value, got {p}")

        self.points = points
        super().__init__(transformation, force_load_on_start, permanent)

        self._height = max(p[1] for p in self.points)
        self._width = max(p[0] for p in self.points)
        self._find_initial_dimension()

        self.texture = texture
        self.texture_top_left = texture_top_left

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
            gfxdraw.textured_polygon(background, self.points, surf, *self.texture_top_left)
            surfaces.append(background)

        self.surfaces = tuple(surfaces)
        self.durations = self.texture.durations
        self.introduction = self.texture.introduction

        if need_to_unload:
            self.texture.unload()

class TexturedCircle(Art):
    """A TexturedCircle is an Art with a textured circle at the center of it."""

    def __init__(
        self,
        radius: int,
        texture: Art,
        center: tuple[int, int] = None,
        draw_top_right: bool = True,
        draw_top_left: bool = True,
        draw_bottom_left: bool = True,
        draw_bottom_right: bool = True,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
    ):
        super().__init__(transformation, force_load_on_start, permanent)
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
        self.surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()

class TexturedEllipse(Art):
    """A TexturedEllipse is an Art with a textured ellipsis at the center of it."""

    def __init__(
        self,
        horizontal_radius: int,
        vertical_radius: int,
        texture: Art,
        center: tuple[int, int] = None,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
    ) -> None:
        super().__init__(transformation, force_load_on_start, permanent)
        if center is None:
            center = texture.width//2, texture.height//2
        self.center = center
        self.rect = (self.center[0] - horizontal_radius, self.center[0] - vertical_radius, horizontal_radius*2, vertical_radius*2)
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
        self.surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()

class TexturedRoundedRectangle(Art):
    """A TexturedRoundedRectangle is an Art with rounded angles."""

    def __init__(
        self,
        texture: Art,
        top_left: int,
        top_right: int = None,
        bottom_left: int = None,
        bottom_right: int = None,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False,
    ):
        super().__init__(transformation, force_load_on_start, permanent)
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
        self.surfaces = tuple(mask.to_surface(setsurface=surface.convert_alpha(), unsetsurface=surf) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()
