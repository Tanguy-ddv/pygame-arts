from typing import Sequence
from pygame import Surface, Rect, Color
from pygamecv import rectangle, line, lines, polygon, circle, ellipse, pie, arc, rounded_rectangle
from ._transformation import Transformation

class DrawCircle(Transformation):
    """Draw a circle on the art."""

    def __init__(
        self,
        color: Color,
        radius: int,
        center: tuple[int, int],
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()

        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.center = center
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            circle(surf, self.center, self.radius, self.color, self.thickness, antialias)
        return surfaces, durations, introduction, None, width, height

class DrawRectangle(Transformation):
    """Draw a rectangle on the art."""
    def __init__(
        self,
        color: Color,
        rect: Rect,
        thickness: int,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()  
        self.color = color
        self.rect = Rect(rect)
        self.allow_antialias = allow_antialias
        self.thickness = thickness

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rectangle(surf, self.rect, self.color, self.thickness)
        return surfaces, durations, introduction, None, width, height

class DrawRoundedRectantle(Transformation):
    """Draw a rectangle on the art, with rounded corners."""
    def __init__(
        self,
        color: Color,
        rect: Rect,
        top_left: int,
        top_right: int = None,
        bottom_right: int = None,
        bottom_left: int = None,
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()  
        self.color = color
        self.rect = Rect(rect)
        self.thickness = thickness
        self.allow_antialias = allow_antialias
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_right = bottom_right
        self.bottom_left = bottom_left

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            rounded_rectangle(surf, self.rect, self.color, self.thickness, antialias, self.top_left, self.top_right, self.bottom_left, self.bottom_right)
        return surfaces, durations, introduction, None, width, height

class DrawEllipse(Transformation):
    """Draw an ellipse on the art."""

    def __init__(
        self,
        color: Color,
        x_radius: int,
        y_radius: int,
        center: tuple[int, int],
        thickness: int = 0,
        angle: int=0,
        allow_antialias: bool = True
    ):
        self.color = color
        self.x_radius = x_radius
        self.y_radius = y_radius
        self.center = center
        self.angle = angle
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            ellipse(surf, self.center, self.x_radius, self.y_radius, self.color, self.thickness, antialias, self.angle)
        return surfaces, durations, introduction, None, width, height

class DrawPolygon(Transformation):
    """Draw a polygon on the art."""

    def __init__(
        self,
        color: Color,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()

        self.color = color
        self.points = points
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            polygon(surf, self.points, self.color, self.thickness, antialias)
        return surfaces, durations, introduction, None, width, height

class DrawLine(Transformation):
    """Draw one line on the art."""

    def __init__(self, color: Color, p1: tuple[int, int], p2: tuple[int, int], thickness: int = 1, allow_antialias: bool = True) -> None:
        self.color = color
        self.p1 = p1
        self.p2 = p2
        self.thickness = thickness
        self.allow_antialias = allow_antialias
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            line(surf, self.p1, self.p2, self.color, self.thickness, antialias)
        return surfaces, durations, introduction, None, width, height

class DrawLines(Transformation):
    """Draw lines on the art."""

    def __init__(self, color: Color, points: Sequence[tuple[int, int]], thickness: int = 1, closed: bool = False, allow_antialias: bool = True) -> None:
        self.color = color
        self.points = points
        self.thickness = thickness
        self.closed = closed
        self.allow_antialias = allow_antialias
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            lines(surf, self.points, self.color, self.thickness, antialias, self.closed)
        return surfaces, durations, introduction, None, width, height

class DrawArc(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: Color,
        ellipsis_center: tuple[int, int],
        horizontal_radius: int,
        vertical_radius: int,
        from_angle: int,
        to_angle: int,
        angle: int = 0,
        thickness: int = 1,
        allow_antialias: bool = True
    ) -> None:
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = horizontal_radius
        self.ry = vertical_radius
        self.from_angle = from_angle
        self.to_angle = to_angle
        self.angle = angle
        self.allow_antialias = allow_antialias

        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            arc(surf, self.ellipsis_center, self.rx, self.ry, self.color, self.thickness, antialias, self.angle, self.from_angle, self.to_angle)

        return surfaces, durations, introduction, None, width, height

class DrawPie(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: Color,
        ellipsis_center: tuple[int, int],
        horizontal_radius: int,
        vertical_radius: int,
        from_angle: int,
        to_angle: int,
        angle: int = 0,
        thickness: int = 1,
        allow_antialias: bool = True
    ) -> None:
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = horizontal_radius
        self.ry = vertical_radius
        self.from_angle = from_angle
        self.to_angle = to_angle
        self.angle = angle
        self.allow_antialias = allow_antialias

        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            pie(surf, self.ellipsis_center, self.rx, self.ry, self.color, self.thickness, antialias, self.angle, self.from_angle, self.to_angle)
        return surfaces, durations, introduction, None, width, height
