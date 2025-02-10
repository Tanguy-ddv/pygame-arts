"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
from math import cos, sin, radians
from random import randint
import pygame.transform as tf
from pygame import Surface, SRCALPHA, Rect, Color

class Transformation(ABC):
    """A transformation is an operation on an art."""

    @abstractmethod
    def apply(
        self,
        surfaces: tuple[Surface],
        durations: tuple[int],
        introduction: int,
        index: int,
        width: int,
        height: int,
        **ld_kwargs
    ):
        """Apply the transformation"""
        raise NotImplementedError()

    def get_new_dimension(self, width, height) -> tuple[int, int]:
        """Calculate the new dimensions of the art after transformation."""
        return width, height

    def cost(self, width, height, length, **ld_kwargs):
        """
        Return the cost of the transformation.
        
        The cost is a numerical metric used to determine whether the transformation
        should be done in the main thread or in a parallel thread.
        """
        return 0

    def __len__(self):
        return 1

class Pipeline(Transformation):
    """A Transformation pipeline is a list of successive transformations."""

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: list[Transformation] = list(transfos).copy()

    def add_transformation(self, transfo: Transformation) -> None:
        """Add a new transformation in the pipeline."""
        self._transformations.append(transfo)

    def clear(self):
        """Clear the Pipeline from all transformations."""
        self._transformations.clear()
    
    def __len__(self):
        return sum(len(transfo) for transfo in self._transformations)
    
    def is_empty(self) -> bool:
        """Return True if the Pipeline is empty of transformations."""
        return not bool(self._transformations)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        successive_indices = []
        for transfo in self._transformations:
            surfaces, durations, introduction, idx, width, height = transfo.apply(surfaces, durations, introduction, index, width, height, **ld_kwargs)
            if idx is not None:
                index = idx
            successive_indices.append(idx)
        # Find the last not None index. If there is no, we return None
        for idx in successive_indices[::-1]:
            if idx is not None:
                break
        return surfaces, durations, introduction, idx, width, height

    def get_new_dimension(self, width, height):
        for transfo in self._transformations:
            width, height = transfo.get_new_dimension(width, height)
        return width, height

    def cost(self, width, height, length, **ld_kwargs):
        return sum(transfo.cost(width, height, length, **ld_kwargs) for transfo in self._transformations)
    
    def copy(self):
        return Pipeline(*self._transformations)

class Rotate(Transformation):
    """The rotate transformation will rotate the art by a given angle."""

    def __init__(self, angle: float) -> None:
        super().__init__()
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        rotated_surfaces = tuple(tf.rotate(surf, self.angle) for surf in surfaces)
        return rotated_surfaces, durations, introduction, None, *rotated_surfaces[0].get_size()

    def get_new_dimension(self, width, height):
        radians_angle = radians(self.angle)
        new_width = abs(width * cos(radians_angle)) + abs(height * sin(radians_angle))
        new_height = abs(width * sin(radians_angle)) + abs(height * cos(radians_angle))
        return int(new_width), int(new_height)


class Zoom(Transformation):
    """
    The zoom transformation will zoom the art by a give scale.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a scale of 1.2 would modify the art
    to a size (120, 120). Calling this transformation with a scale of 0.6 would modify the art
    to a size (60, 60). You can also specify two scales (one for horizontal and one for vertical) by passing
    a tuple as scale. If smooth is True, use a smooth zooming instead.
    """

    def __init__(self, scale: float | tuple[float, float], smooth: bool = False) -> None:
        super().__init__()
        self.scale = scale
        self.smooth = smooth

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if (self.scale == (2, 2) or self.scale == 2) and not self.smooth:
            rescaled_surfaces = tuple(tf.scale2x(surf) for surf in surfaces)
        elif not self.smooth:
            rescaled_surfaces = tuple(tf.scale_by(surf, self.scale) for surf in surfaces)
        else:
            rescaled_surfaces = tuple(tf.smoothscale_by(surf, self.scale) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, None, int(width*self.scale), int(height*self.scale)

    def get_new_dimension(self, width, height):
        return int(width*self.scale), int(height*self.scale)

class Resize(Transformation):
    """
    The resize transformation will resize the art to a new size. The image might end distorded.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a zie of (120, 60) would modify the art
    to a size (120, 60). If smooth is True, use a smooth resizing instead.
    """

    def __init__(self, size: tuple[int, int], smooth: bool = False) -> None:
        super().__init__()
        self.size = size
        self.smooth = smooth

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.smooth:
            rescaled_surfaces = tuple(tf.smoothscale(surf, self.size) for surf in surfaces)
        else:
            rescaled_surfaces = tuple(tf.scale(surf, self.size) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, None, *self.size

    def get_new_dimension(self, width, height):
        return self.size

class Crop(Transformation):
    """
    The crop transformation crop the art to a smaller art.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with left=50, top=50, width=20, height=30 will result
    in a surface with only the pixels from (50, 50) to (70, 80)
    """

    def __init__(self, left: int, top: int, width: int, height: int) -> None:
        super().__init__()
        self.rect = Rect(left, top, width, height)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        background = Surface(self.rect.size)
        cropped_surfaces = []
        for surf in surfaces:
            background.blit(surf, (0,0), self.rect)
            cropped_surfaces.append(background.copy())
        return tuple(cropped_surfaces), durations, introduction, None, *self.rect.size

    def get_new_dimension(self, width, height):
        return self.rect.size

class Pad(Transformation):
    """
    The pad transformation add a solid color extension on every side of the art. If the pad is negative, act like a crop.
    """

    def __init__(self, color: Color, left: int = 0, right = 0, top = 0, bottom = 0) -> None:
        super().__init__()
        self.color = color
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        background = Surface((width + self.left + self.right, height + self.left + self.right), SRCALPHA)
        background.fill(self.color)
        padded_surfaces = []
        for surf in surfaces:
            background.blit(surf, (self.left, self.top))
            padded_surfaces.append(background.copy())
        return tuple(padded_surfaces), durations, introduction, None, width + self.left + self.right, height + self.left + self.right

    def get_new_dimension(self, width, height):
        return width + self.left + self.right, height + self.left + self.right

class Flip(Transformation):
    """
    The flip transformation flips the art, horizontally and/or vertically.
    """

    def __init__(self, horizontal: bool, vertical: bool) -> None:
        super().__init__()
        self.horizontal = horizontal
        self.vertical = vertical

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        flipped_surfaces = tuple(tf.flip(surf, self.horizontal, self.vertical) for surf in surfaces)
        return flipped_surfaces, durations, introduction, None, height, width

    def get_new_dimension(self, width, height):
        return width, height

class Transpose(Transformation):
    """The transpose transformation transpose the art like a matrix."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        tp_surfaces = tuple(tf.flip(tf.rotate(surf, 270), True, False) for surf in surfaces)
        return tp_surfaces, durations, introduction, None, width, height

    def get_new_dimension(self, width, height):
        return height, width

class VerticalChop(Transformation):
    """
    The vertical chop transformation remove a band of pixel and put the right side next to the left side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (from_, 0, to - from_, 0)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        chopped_surfaces = tuple(tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, None, width - self.rect[2], height

    def get_new_dimension(self, width, height):
        return width - self.rect[2], height

class HorizontalChop(Transformation):
    """
    The horizontal chop transformation remove a band of pixel and put the bottom side just below to the top side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (0, from_, 0, to - from_)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        chopped_surfaces = tuple(tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, None, width, height - self.rect[3]

    def get_new_dimension(self, width, height):
        return width, height - self.rect[3]

class SpeedUp(Transformation):
    """
    Speed up the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 50 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        new_durations = tuple(d/self.scale for d in durations)
        return surfaces, new_durations, introduction, None, width, height

class SlowDown(Transformation):
    """
    Slow down the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 200 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        new_durations = tuple(d*self.scale for d in durations)
        return surfaces, new_durations, introduction, None, width, height

class ResetDuration(Transformation):
    """
    Reset the duration of every image in the art to a new value.
    """

    def __init__(self, new_duration: int) -> None:
        super().__init__()
        self.new_duration = new_duration

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return surfaces, tuple(self.new_duration for _ in durations), introduction, None, width, height

class ResetDurations(Transformation):
    """
    Reset the durations of every image in the art to new values.
    """

    def __init__(self, new_durations: tuple[int]) -> None:
        super().__init__()
        self.new_durations = new_durations

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return surfaces, tuple(self.new_durations[i%len(self.new_durations)] for i, _ in enumerate(durations)), introduction, None, width, height

class SetIntroductionIndex(Transformation):
    """
    Set the introduction to a new index.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return surfaces, durations, self.introduction, None, width, height

class SetIntroductionTime(Transformation):
    """
    Set the introduction to a new index by specifying a time.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):

        sum_dur = 0
        new_intro_idx = 0
        while sum_dur < self.introduction and new_intro_idx < len(durations):
            sum_dur += durations[new_intro_idx]
            new_intro_idx += 1

        return surfaces, durations, new_intro_idx, None, width, height

def _index_here(index, length, introduction):
    if index < length:
        return index
    else:
        return _index_here(index - length + introduction, length, introduction)

class ExtractSlice(Transformation):
    """
    This transformation returns a subset of the images and durations of the art. Bounds are included
    """

    def __init__(self, slice: slice) -> None:
        super().__init__()
        self.slice = slice

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        # Allow calling for indexing further than the number of surfaces, in this case, get the surfaces after having avoided the introduction.
        # Ex: ExtractSlice(slice(10, 19)) on a art with len(art) = 15 and introduction = 7 returns the surfaces at indices [10, 11, 12, 13, 14, 7, 8, 9]
        indices = range(*self.slice.indices(len(surfaces)*2 - introduction))
        surfaces = tuple(surfaces[_index_here(index, len(surfaces), introduction)] for index in indices)
        durations = tuple(durations[_index_here(index, len(durations), introduction)] for index in indices)
        return surfaces, durations, 0, 0, width, height

class ExtractOne(Transformation):
    """Extract one frame of the animation."""

    def __init__(self, index: int) -> None:
        super().__init__()
        self.index = index

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):

        return (surfaces[_index_here(self.index, len(surfaces), introduction)],), (0,), 0, 0, width, height

class First(Transformation):
    """Extract the very first frame of the animation."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return (surfaces[0],), (0,), 0, 0, width, height

class Last(Transformation):
    """Extract the very last frame of the animation."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return (surfaces[-1],), (0,), 0, 0, width, height

class ExtractAtIntroduction(Transformation):

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return (surfaces[introduction],), (0,), 0, 0, width, height

class ExtractTime(Transformation):
    """Extract the frame appearing at a given time."""

    def __init__(self, time: int) -> None:
        super().__init__()
        self.time = time
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        cum_time = 0
        idx = 0
        next_idx = 1

        while self.time >= cum_time + durations[next_idx]:
            cum_time += durations[next_idx]
            idx += 1
            if idx == len(surfaces):
                idx = introduction
            next_idx += 1
            if next_idx == len(surfaces):
                next_idx = introduction
        return (surfaces[idx],), (0,), 0, 0, width, height

class ExtractWindow(Transformation):

    def __init__(self, from_time: int, to_time: int):
        super().__init__()

        self.from_time = from_time
        self.to_time = to_time

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        cum_time = 0
        idx = 0
        next_idx = 1

        while self.from_time >= cum_time + durations[next_idx]:
            cum_time += durations[next_idx]
            idx += 1
            if idx == len(surfaces):
                idx = introduction
            next_idx += 1
            if next_idx == len(surfaces):
                next_idx = introduction

        surfs = [surfaces[idx]]
        durs = [durations[idx]]
        indices = [idx]

        while self.to_time >= cum_time + durations[next_idx]:
            cum_time += durations[next_idx]
            idx += 1
            if idx == len(surfaces):
                idx = introduction
            next_idx += 1
            if next_idx == len(surfaces):
                next_idx = introduction
            surfs.append(surfaces[idx])
            durs.append(durations[idx])
            indices.append(idx)
        
        if introduction not in indices: introduction = 0
        else: introduction = introduction - min(indices)

        if index not in indices: index = 0
        else: index = index - min(indices)

        return surfs, durs, introduction, index, width, height

class RandomizeIndex(Transformation):

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        return surfaces, durations, introduction, randint(len(surfaces)), width, height