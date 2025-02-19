"""The drawing module contains the drawing transformations."""
from typing import Sequence
from pygame import Surface, Rect
from pygamecv import rectangle, line, lines, polygon, circle, ellipse, pie, arc, rounded_rectangle
from .transformation import Transformation
from .._common import ColorValue

class DrawCircle(Transformation):
    """Draw a circle on the art."""

    def __init__(
        self,
        color: ColorValue,
        radius: int,
        center: tuple[int, int],
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw a circle on the art.

        Params:
        ----
        - color: ColorValue, the color used to draw the circle. It can have an alpha channel != 255.
        - radius: int, the radius of the circle
        - center: tuple[int, int], the center of the circle
        - thickness: int, the thickness of the line used to draw the circle. If 0, the circle is filled.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
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
    
    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        if self.color.a == 255 and not ld_kwargs.get("antialias", False):
            return self.radius**2*4*length
        else:
            return self.radius**2*4*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawRectangle(Transformation):
    """Draw a rectangle on the art."""
    def __init__(
        self,
        color: ColorValue,
        rect: Rect,
        thickness: int,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw a rectangle on the art.

        Params:
        ---
        - color: ColorValue, the color used to draw the rectangle. It can have an alpha channel != 255.
        - rect: pygame.Rect, the rectangle representing the edges of the rectangle.
        - thickness: int, the thickness of the line used to draw the rectangle. If 0, the rectangle is filled.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """

        super().__init__()  
        self.color = color
        self.rect = Rect(rect)
        self.allow_antialias = allow_antialias
        self.thickness = thickness

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rectangle(surf, self.rect, self.color, self.thickness)
        return surfaces, durations, introduction, None, width, height

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        if self.color.a == 255 and not ld_kwargs.get("antialias", False):
            return self.rect.width*self.rect.height*length
        else:
            return self.rect.width*self.rect.height*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawRoundedRectangle(Transformation):
    """Draw a rectangle on the art, with rounded corners."""
    def __init__(
        self,
        color: ColorValue,
        rect: Rect,
        top_left: int,
        top_right: int = None,
        bottom_right: int = None,
        bottom_left: int = None,
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw a rectangle on the art, with rounded corners.

        Params:
        ---
        - color: ColorValue, the color used to draw the rounded rectangle. It can have an alpha channel != 255.
        - rect: pygame.Rect, the rectangle representing the edges of the rectangle.
        - top_left, top_right, bottom_left, bottom_right: the radii of the rounded corners.
        If one of the 3 last is None, the value for the top_left corner is used instead.
        - thickness: int, the thickness of the line used to draw the rounded rectangle. If 0, the rounded rectangle is filled.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        if self.color.a == 255 and (not ld_kwargs.get("antialias", False) or self.top_right == self.top_left == self.bottom_right == self.bottom_left == 0) and (
        # Condition to pygame.draw in pygame.CV
            self.top_right + self.top_left <= self.rect.width//2
            and self.bottom_left + self.bottom_right <= self.rect.width//2
            and self.top_right + self.bottom_right <= self.rect.height//2
            and self.top_left + self.bottom_left <= self.rect.height//2
        ):
            return self.rect.width*self.rect.height*length
        else:
            return self.rect.width*self.rect.height*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawEllipse(Transformation):
    """Draw an ellipse on the art."""

    def __init__(
        self,
        color: ColorValue,
        radius_x: int,
        radius_y: int,
        center: tuple[int, int],
        thickness: int = 0,
        angle: int=0,
        allow_antialias: bool = True
    ):
        """
        Draw an ellipse on the art.

        Params:
        ----
        - color: ColorValue, the color used to draw the ellipse. It can have an alpha channel != 255.
        - radius_x: int, the horizontal radius of the ellipse, before rotation.
        - radius_y: int, the vertical radius of the ellipse, before rotation.
        - center: tuple[int, int], the center of the ellipse
        - thickness: int, the thickness of the line used to draw the ellipse. If 0, the ellipse is filled.
        - angle: int = 0, the angle in degrees by which the ellipse should be rotated, counterclockwise.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
        self.color = color
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.center = center
        self.angle = angle
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        antialias = self.allow_antialias and ld_kwargs.get("antialias", False)
        for surf in surfaces:
            ellipse(surf, self.center, self.radius_x, self.radius_y, self.color, self.thickness, antialias, self.angle)
        return surfaces, durations, introduction, None, width, height

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        if self.color.a == 255 and not ld_kwargs.get("antialias", False):
            return self.radius_x*self.radius_y*4*length
        else:
            return self.radius_x*self.radius_y*4*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawPolygon(Transformation):
    """Draw a polygon on the art."""

    def __init__(
        self,
        color: ColorValue,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw a polygon on the art.

        Params:
        ---
        - color: ColorValue, the color used to draw the polygon. It can have an alpha channel != 255.
        - points: Sequence[tuple[int, int]], the sequence of points.
        - thickness: int, the thickness of the line used to draw the polygon. If 0, the polygon is filled.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        left = min(point[0] for point in self.points) - self.thickness//2
        right = max(point[0] for point in self.points) + self.thickness//2 +1
        top = min(point[1] for point in self.points) - self.thickness//2
        bottom = max(point[1] for point in self.points) + self.thickness//2 + 1
        width = right - left +1
        height = bottom - top +1
        return width*height*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawLine(Transformation):
    """Draw one line on the art."""

    def __init__(self, color: ColorValue, p1: tuple[int, int], p2: tuple[int, int], thickness: int = 1, allow_antialias: bool = True) -> None:
        """
        Draw one line on the art.
        
        Params:
        ---
        - color: ColorValue, the color used to draw the line. It can have an alpha channel != 255.
        - p1: tuple[int, int], the position of start of the line.
        - p2: tuple[int, int], the position of the end of the line.
        - thickness: int, the thickness of the line used to draw the line.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """

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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        left = min(self.p1[0], self.p2[0]) - self.thickness//2
        right = max(self.p1[0], self.p2[0]) + self.thickness//2 
        top = min(self.p1[1], self.p2[1]) - self.thickness//2
        bottom = max(self.p1[1], self.p2[1]) + self.thickness//2
        width = right - left + 1
        height = bottom - top + 1
        return width*height*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawLines(Transformation):
    """Draw lines on the art."""

    def __init__(self, color: ColorValue, points: Sequence[tuple[int, int]], thickness: int = 1, closed: bool = False, allow_antialias: bool = True) -> None:
        """
        Draw lines on the art. This is faster than drawing the lines one by one.

        Params:
        ---
        - color: ColorValue, the color used to draw the lines. It can have an alpha channel != 255.
        - points: Sequence[tuple[int, int]], the sequence of points.
        - thickness: int, the thickness of the line used to draw the lines.
        - closed: bool, If True, the last points is linked to the first point with a line.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        left = min(point[0] for point in self.points) - self.thickness//2
        right = max(point[0] for point in self.points) + self.thickness//2 +1
        top = min(point[1] for point in self.points) - self.thickness//2
        bottom = max(point[1] for point in self.points) + self.thickness//2 + 1
        width = right - left +1
        height = bottom - top +1
        return width*height*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawArc(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: ColorValue,
        radius_x: int,
        radius_y: int,
        ellipsis_center: tuple[int, int],
        from_angle: int,
        to_angle: int,
        thickness: int = 1,
        angle: int = 0,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw an arc on the art. An arc is a part of an ellipse.

        Params:
        ----
        - color: ColorValue, the color used to draw the arc. It can have an alpha channel != 255.
        - radius_x: int, the horizontal radius of the ellipse, before rotation.
        - radius_y: int, the vertical radius of the ellipse, before rotation.
        - ellipsis_center: tuple[int, int], the center of the ellipse.
        - from_angle: the starting angle of the arc, in degrees
        - to_angle: the ending angle of the arc, in degrees. The arc is drawn counterclockwise.
        - thickness: int, the thickness of the line used to draw the arc. If 0, a filled pie is drawn.
        - angle: int = 0, the angle in degrees by which the ellipse should be rotated, counterclockwise.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = radius_x
        self.ry = radius_y
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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        return self.rx*self.ry*4*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.

class DrawPie(Transformation):
    """Draw a pie on the art."""

    def __init__(
        self,
        color: ColorValue,
        radius_x: int,
        radius_y: int,
        ellipsis_center: tuple[int, int],
        from_angle: int,
        to_angle: int,
        thickness: int = 1,
        angle: int = 0,
        allow_antialias: bool = True
    ) -> None:
        """
        Draw a pie on the art. A pie is an arc where the start and end points are linked to the center of the ellipse.

        Params:
        ----
        - color: ColorValue, the color used to draw the pie. It can have an alpha channel != 255.
        - radius_x: int, the horizontal radius of the ellipse, before rotation.
        - radius_y: int, the vertical radius of the ellipse, before rotation.
        - ellipsis_center: tuple[int, int], the center of the ellipse.
        - from_angle: the starting angle of the arc, in degrees
        - to_angle: the ending angle of the arc, in degrees. The arc is drawn counterclockwise.
        - thickness: int, the thickness of the line used to draw the pie. If 0, the pie is filled.
        - angle: int = 0, the angle in degrees by which the ellipse should be rotated, counterclockwise.
        - allow_antialias: bool = True, if False, even with 'antialias' : True as a loading kwarg, the drawing will be done without antialias.
        """

        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = radius_x
        self.ry = radius_y
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

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        return self.rx*self.ry*4*length*4 # Once for the color draw, twice for the apha rendering (copy and addWeighted) and once for the final blit.
