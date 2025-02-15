"""This mask submodule contains the bases for masks and geometrical masks."""

from abc import ABC, abstractmethod
from ZOCallable import ZOZOCallable, verify_ZOZOCallable
from ZOCallable.functions import linear
import numpy as np
from pygame import Surface, surfarray as sa, SRCALPHA, draw, Rect
from .._error import LoadingError


class Mask(ABC):
    """Mask is an abstract class for all masks."""

    def __init__(self) -> None:
        super().__init__()
        self._loaded = False
        self.matrix: np.ndarray = None

    @abstractmethod
    def _load(self, width: int, height: int, **ld_kwargs):
        raise NotImplementedError()

    def load(self, width: int, height: int, **ld_kwargs):
        """Load the mask."""
        self._load(width, height,**ld_kwargs)
        self._loaded = True

    def unload(self):
        """Unload the mask."""
        self.matrix = None
        self._loaded = False

    def is_loaded(self):
        """Return True if the mask is loaded, False otherwise."""
        return self._loaded

    def not_null_columns(self):
        """Return the list of indices of the columns that have at least one value different from 0."""
        if self.is_loaded():
            return np.where(self.matrix.any(axis=0))[0]
        raise LoadingError("Unloaded masks do not have any matrix and so not null columns.")

    def not_null_rows(self):
        """Return the list of indices of the rows that have at least one value different from 0."""
        if self.is_loaded():
            return np.where(self.matrix.any(axis=1))[0]
        raise LoadingError("Unloaded masks do not have any matrix and so not null rows.")

    def is_empty(self):
        """Return True if all the pixels in the mask are set to 0."""
        if self.is_loaded():
            return np.sum(self.matrix) == 0
        raise LoadingError("Unloaded masks cannot be empty.")


    def is_full(self):
        """Return True if all the pixels in the mask are set to 1."""
        if self.is_loaded():
            return np.sum(self.matrix) == self.matrix.size
        raise LoadingError("Unloaded masks cannot be full.")

class MatrixMask(Mask):
    """A matrix mask is a mask based on a matri, this matrix can be changed."""

    def __init__(self, matrix: np.ndarray) -> None:
        super().__init__()
        self._matrix = np.clip(matrix, 0, 1)

    def _load(self, width: int, height: int, **ld_kwargs):
        """Pad and crop the matrix to match the size."""
        self.matrix = np.pad(
            self._matrix, [
                (0, max(0, width - self._matrix.shape[0])),
                (0, max(0, height - self._matrix.shape[1]))
            ],
            'edge'
        )[: width, :height]
    
    def update_matrix(self, new_matrix: np.ndarray):
        """Update the current matrix with a user-defined matrix. Both matrices should have the same shape."""
        self._matrix = new_matrix
        self._load(*self.matrix.shape)

class Circle(Mask):
    """A Circle is a mask with two values: 0 in the circle and 1 outside."""

    def __init__(self, radius: float | int, center: tuple[float, float] | tuple[int, int] = (0.5, 0.5)):
        super().__init__()
        self.radius = radius
        self.center = center

    def _load(self, width: int, height: int, **ld_kwargs):
        grid_x, grid_y = np.ogrid[:width, :height]
        center = (
            self.center[0]*width if 0 <= self.center[0] <= 1 else self.center[0],
            self.center[1]*height if 0 <= self.center[1] <= 1 else self.center[1]
        )
        distances = np.sqrt((grid_x - center[0] - 0.5) ** 2 + (grid_y - center[1] - 0.5) ** 2)
        radius = self.radius*min(height, width) if  0 <= self.radius <= 1 else self.radius
        self.matrix = (distances > radius).astype(int)

class Ellipse(Mask):
    """An Ellipsis is a mask with two values: 0 in the ellipsis and 1 outside."""

    def __init__(self, radius_x: int | float, radius_y: int | float, center: tuple[int, int] | tuple[float, float] = (0.5, 0.5)):
        super().__init__()
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.center = center

    def _load(self, width: int, height: int, **ld_kwargs):
        grid_y, grid_x = np.ogrid[:height, :width]
        center = (
            self.center[0]*width if 0 <= self.center[0] <= 1 else self.center[0],
            self.center[1]*height if 0 <= self.center[1] <= 1 else self.center[1]
        )
        radius_x = self.radius_x*width if  0 <= self.radius_x <= 1 else self.radius_x
        radius_y = self.radius_y*height if  0 <= self.radius_y <= 1 else self.radius_y
        distances = np.sqrt((grid_x - center[0] - 0.5) ** 2 / radius_x**2 + (grid_y - center[1] - 0.5) ** 2 / radius_y**2)

        self.matrix = (distances > 1).astype(int)

class Rectangle(Mask):
    """A Rectangle is a mask with two values: 0 inside the rectangle and 1 outside."""

    def __init__(self, left: int | float, top: int | float, right: int | float, bottom: int | float):
        """
        A Rectangle is a mask with two values: 0 inside the rectangle and 1 outside.
        
        Params:
        ----
        - left: int, the coordinate of the left of the rectangle, included.
        - top: int, the coordinate of the top of the rectangle, included.
        - right: int, the coordinate of the right of the rectangle, included.
        - bottom: int, the coordinate of the bottom of the rectangle, included.

        Example:
        ----
        >>> r = Rectangle(6, 4, 2, 1, 4, 5)
        >>> r.load(settings)
        >>> print(r.matrix)
        >>> [[1 1 1 1 1 1]
             [1 1 0 0 0 1]
             [1 1 0 0 0 1]
             [1 1 1 1 1 1]]
        """

        super().__init__()
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def _load(self, width:int, height:int, **ld_kwargs):
        grid_y, grid_x = np.ogrid[:height, :width]
        left = self.left*width if 0 <= self.left <= 1 and isinstance(self.left, float) else self.left
        right = self.right*width if 0 <= self.right <= 1 and isinstance(self.right, float) else self.right
        top = self.top*height if 0 <= self.top <= 1 and isinstance(self.top, float) else self.top
        bottom = self.bottom*height if 0 <= self.bottom <= 1 and isinstance(self.bottom, float) else self.bottom
        self.matrix = 1 - ((left <= grid_x) & (grid_x <= right) & (top <= grid_y) & (grid_y <= bottom)).astype(int)

class Polygon(Mask):
    """
    A Polygon is a mask with two values: 0 inside the polygon and 1 outside the polygon.
    The Polygon is defined from a list of points. If points are outside of [0, width] x [0, height],
    the polygon is cropped.
    """

    def __init__(self, points: list[tuple[int, int]]) -> None:
        super().__init__()

        self.points = points

    def _load(self, width: int, height: int, **ld_kwargs):
        surf = Surface((width, height), SRCALPHA)
        draw.polygon(surf, (0, 0, 0, 255), self.points)
        self.matrix = 1 - sa.array_alpha(surf)/255

class RoundedRectangle(Mask):
    """A RoundedRectangle mask is a mask with two values: 0 inside of the rectangle with rounded vertexes, and 1 outside."""

    def __init__(self, left: int | float, top: int | float, right: int | float, bottom: int | float, radius: int):
        super().__init__()
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.radius = radius

    def _load(self, width: int, height: int, **ld_kwargs):
        surf = Surface((width, height), SRCALPHA)
        left = self.left*width if 0 <= self.left <= 1 and isinstance(self.left, float) else self.left
        right = self.right*width if 0 <= self.right <= 1 and isinstance(self.right, float) else self.right
        top = self.top*height if 0 <= self.top <= 1 and isinstance(self.top, float) else self.top
        bottom = self.bottom*height if 0 <= self.bottom <= 1 and isinstance(self.bottom, float) else self.bottom
        draw.rect(surf, (0, 0, 0, 255), Rect(left, top, right - left + 1, bottom - top + 1), 0, self.radius)
        self.matrix = 1 - sa.array_alpha(surf)/255

class GradientCircle(Mask):
    """
    A GradientCircle mask is a mask where the values ranges from 0 to 1. All pixels in the inner circle are set to 0,
    all pixels out of the outer cirlce are set to 1, and pixels in between have an intermediate value.

    The intermediate value is defined by the transition function. This function must be vectorized.
    """

    def __init__(
            self,
            inner_radius: int | float,
            outer_radius: int | float = 1.,
            transition: ZOZOCallable = linear,
             center: tuple[float, float] | tuple[int, int] = (0.5, 0.5)
        ):
        super().__init__()
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        if not verify_ZOZOCallable(transition, test_vectorizaiton=True):
            raise ValueError("The provided transition isn't a ZOZOCallable.")
        self.transition = transition
        self.center = center

    def _load(self, width:int, height: int, **ld_kwargs):
        grid_x, grid_y = np.ogrid[:width, :height]

        center = (
            self.center[0]*width if 0 <= self.center[0] <= 1 else self.center[0],
            self.center[1]*height if 0 <= self.center[1] <= 1 else self.center[1]
        )
        distances = np.sqrt((grid_x - center[0] - 0.5) ** 2 + (grid_y - center[1] - 0.5) ** 2)
        inner_radius = self.inner_radius*min(height, width) if  0 <= self.inner_radius <= 1 else self.inner_radius
        outer_radius = self.outer_radius*min(height, width) if  0 <= self.outer_radius <= 1 else self.outer_radius
        distances = np.sqrt((grid_x - center[0] - 0.5) ** 2 + (grid_y - center[1] - 0.5) ** 2)
        self.matrix = np.clip((distances - inner_radius)/(outer_radius - inner_radius), 0, 1)
        self.matrix = self.transition(self.matrix)

class GradientRectangle(Mask):
    """
    A GradientRectangle mask is a mask where values range from 0 to 1. All pixels inside the inner rectangle are set to 0.
    All pixels outside the outer rectangle are set to 1. All pixels in between have an intermediate value.

    The intermediate value is defined by the transition function.
    """

    def __init__(
        self,
        inner_left: int,
        inner_right: int,
        inner_top: int,
        inner_bottom: int,
        outer_left: int = 0.,
        outer_right: int = 1.,
        outer_top: int = 0.,
        outer_bottom: int = 1.,
        transition: ZOZOCallable = linear
    ):

        super().__init__()

        if outer_bottom < inner_bottom or outer_top > inner_top or outer_left > inner_left or outer_right < inner_right:
            raise ValueError(
                f"""The outer rectangle cannot be inside of the inner rectangle, got
                inner = ({inner_left, inner_right, inner_top, inner_bottom})
                and outer = ({outer_left, outer_right, outer_top, outer_bottom})"""
            )

        self.inner_left = inner_left
        self.inner_right = inner_right
        self.inner_bottom = inner_bottom
        self.inner_top = inner_top

        self.outer_left = outer_left
        self.outer_right = outer_right
        self.outer_bottom = outer_bottom
        self.outer_top = outer_top

        verify_ZOZOCallable(transition, test_vectorizaiton=True)
        self.transition = transition

    def _load(self, width: int, height: int, **ld_kwargs):
        y_indices, x_indices = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        inner_left = self.inner_left*width if 0 <= self.inner_left <= 1 and isinstance(self.inner_left, float) else self.inner_left
        inner_right = self.inner_right*width if 0 <= self.inner_right <= 1 and isinstance(self.inner_right, float) else self.inner_right
        inner_top = self.inner_top*height if 0 <= self.inner_top <= 1 and isinstance(self.inner_top, float) else self.inner_top
        inner_bottom = self.inner_bottom*height if 0 <= self.inner_bottom <= 1 and isinstance(self.inner_bottom, float) else self.inner_bottom

        outer_left = self.outer_left*width if 0 <= self.outer_left <= 1 and isinstance(self.outer_left, float) else self.outer_left
        outer_right = self.outer_right*width if 0 <= self.outer_right <= 1 and isinstance(self.outer_right, float) else self.outer_right
        outer_top = self.outer_top*height if 0 <= self.outer_top <= 1 and isinstance(self.outer_top, float) else self.outer_top
        outer_bottom = self.outer_bottom*height if 0 <= self.outer_bottom <= 1 and isinstance(self.outer_bottom, float) else self.outer_bottom

        left_dist = np.clip((inner_left - x_indices) / (inner_left - self.outer_left + 1), 0, 1)
        right_dist = np.clip((x_indices - inner_right) / (outer_right - self.inner_right + 1), 0, 1)
        top_dist = np.clip((inner_top - y_indices) / (inner_top - outer_top + 1), 0, 1)
        bottom_dist = np.clip((y_indices - inner_bottom) / (outer_bottom - inner_bottom + 1), 0, 1)

        self.matrix = self.transition(np.clip(np.sqrt(left_dist**2 + right_dist**2 + top_dist**2 + bottom_dist**2), 0, 1))
