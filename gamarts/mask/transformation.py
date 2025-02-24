"""The transformation submodule contains all masks being transformations of an image, array or of another mask."""
from abc import ABC, abstractmethod
from typing import Callable, Sequence
from  pygame import surfarray as sa, transform as tf, image as im
import numpy as np
from .mask import Mask


class FromArtAlpha(Mask):
    """A mask from the alpha layer of an art."""

    def __init__(self, art, index: int= 0) -> None:
        """
        A mask from the alpha layer of an art.
        
        Params:
        ---
        - art: Art, the art whose alpha layer is used. A rescaled copy is used if the width and height of the art isn't matching the requested width and height.
        - index: int. The index of the frame to be used in the art.

        Notes:
        ---
        - If the art isn't loaded when the loading of this mask happens, the art will be loaded, then unloaded.
        """
        super().__init__()
        self.art = art
        self.index = index

    def _load(self, width: int, height: int, **ld_kwargs):
        need_to_unload = False
        if not self.art.is_loaded():
            need_to_unload = True
            self.art.load(**ld_kwargs)

        self.matrix = 1 - sa.array_alpha(tf.scale(self.art.surfaces[self.index], (width, height)).convert_alpha()).astype(np.int8)/255

        if need_to_unload:
            self.art.unload()

class FromArtColor(Mask):
    """
    A mask from a mapping of the color layers.
    
    Every pixel of the art is mapped to a value between 0 and 1 with the provided function.
    Selects only one image of the art based on the index.
    """

    def __init__(self, art, function: Callable[[int, int, int], float], index: int = 0) -> None:
        """
        A mask from the color layers of an art.
        
        Params:
        ---
        - art: Art, the art whose color layers is used. A rescaled copy is used if the width and height of the art isn't matching the requested width and height.
        - function: Callable[[int, int, int], float]: A function mapping an rgb tuple to a float between 0 and 1.
        - index: int. The index of the frame to be used in the art.

        Notes:
        ---
        - If the art isn't loaded when the loading of this mask happens, the art will be loaded, then unloaded.
        """
        super().__init__()
        self.art = art
        self.index = index
        self.map = function

    def _load(self, width: int, height: int, **ld_kwargs):
        need_to_unload = False
        if not self.art.is_loaded():
            need_to_unload = True
            self.art.load(**ld_kwargs)

        self.matrix = np.apply_along_axis(lambda t: self.map(*t), 2, sa.array3d(tf.scale(self.art.surfaces[self.index], (width, height))).astype(np.int64))

        if need_to_unload:
            self.art.unload()

class FromImageColor(Mask):
    """
    A mask from an image.
    
    Every pixel of the art is mapped to a value between 0 and 1 with the provided function.
    """

    def __init__(self, path: str, function: Callable[[int, int, int], float]) -> None:
        """
        A mask from an image.

        Params:
        ---
        - path: the path to the image.
        - function: Callable[[int, int, int], float]: A function mapping an rgb tuple to a float between 0 and 1.
        """
        self.path = path
        super().__init__()
        self.map = function

    def _load(self, width: int, height: int, **ld_kwargs):
        rgb_array = sa.array3d(tf.scale(im.load(self.path), (width, height)))
        self.matrix = np.apply_along_axis(lambda t: self.map(*t), 2, rgb_array.astype(np.int64))

class InvertedMask(Mask):
    """
    An inverted mask is a mask whose value are the opposite of the parent mask.
    """

    def __init__(self, mask: Mask):
        """
        An inverted mask is a mask whose value are the opposite of the parent mask.

        Params:
        ---
        - mask: Mask, the mask to be inverted.
        """
        super().__init__()
        self._mask = mask

    def _load(self, width:int, height: int, **ld_kwargs):
        if not self._mask.is_loaded():
            self._mask.load(width, height, **ld_kwargs)
        self.matrix = 1 - self._mask.matrix

class TransformedMask(Mask):
    """
    A Transformed mask is a mask whose matrix is the transformation of the matrix of another mask.
    The transformation must be a numpy vectorized function or a function matrix -> matrix.
    """

    def __init__(self, mask: Mask, transformation: Callable[[float], float] | Callable[[np.ndarray], np.ndarray]):
        """
        Create a mask from the transformation of another mask.
        
        Params:
        ---
        - mask: Mask, the mask to be transformed
        - transformation: Callable[[float], float] | Callable[[numpy.ndarray], numpy.ndarray]: The transformation applied to the mask.
        The transformation create an array from another. Both arrays must have the same shape.
        """
        super().__init__()
        self._mask = mask
        self.transformation = transformation

    def _load(self, width:int, height: int, **ld_kwargs):
        if not self._mask.is_loaded():
            self._mask.load(width, height, **ld_kwargs)

        self.matrix = np.clip(self.transformation(self._mask.matrix), 0, 1)
        if self.matrix.shape != self._mask.matrix.shape:
            raise ValueError(f"Shape of the mask changed from {self._mask.matrix.shape} to {self.matrix.shape}")

class BinaryMask(Mask):
    """
    A binary mask is a mask where every values are 0 or 1. It is based on another mask.
    The matrix of this mask is that every component is 1 if the value on the parent mask
    is above a thresold and 0 otherwise. (this is reversed if reverse is set to True).
    """

    def __init__(self, mask: Mask, threshold: float, reverse: bool = False):
        """
        Create a binary mask.
        
        Params:
        ---
        - mask: the mask to be binarized
        - threshold: the threshold used to compare the values.
        - reverse: flag used to know if the 1 of the binary mask are above the threshold (not reversed) or below the threshold (reversed)
        """

        super().__init__()
        self.threshold = threshold
        self._mask = mask
        self.reverse = reverse

    def _load(self, width:int, height: int, **ld_kwargs):
        if not self._mask.is_loaded():
            self._mask.load(width, height, **ld_kwargs)

        if self.reverse:
            positions_to_keep = self._mask.matrix < self.threshold
        else:
            positions_to_keep = self._mask.matrix > self.threshold

        self.matrix = np.zeros_like(self._mask.matrix)
        self.matrix[positions_to_keep] = 1
