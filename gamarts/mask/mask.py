"""This mask submodule contains the bases for masks and geometrical masks."""
from abc import ABC, abstractmethod
import numpy as np
from typing import Sequence
from .._common import LoadingError

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
        """
        Load the mask. If the mask is already loaded, do nothing.
        
        Params:
        ----
        - width, height: the dimension of the mask.
        - **ld_kwargs: the loading kwargs.
        """
        if not self._loaded:
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
        """
        Return the list of indices of the columns that have at least one value different from 0.
        
        Returns:
        ----
        - list[int], the list of indices of the columns having at least one non-zero value.

        Raises:
        ----
        LoadingError if the mask isn't loaded yet.
        """
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

    def __add__(self, other: 'Mask' | float | int):
        if isinstance(other, Mask):
            return SumOfMasks(self, other)
        elif isinstance(other, (float, int)):
            return _AddedMask(self, other)
        else:
            raise TypeError(f"Only masks and numbers can be added to masks, not {type(other)}")

    def __radd__(self, other: 'Mask' | float | int):
        return self.__add__(other)

    def __mul__(self, other: 'Mask' | float | int):
        if isinstance(other, Mask):
            return ProductOfMasks(self, other)
        elif isinstance(other, (float, int)):
            return _MultipliedMask(self, other)
        else:
            raise TypeError(f"Only masks and numbers can be multiplied to masks, not {type(other)}")
    
    def __rmul__(self, other: 'Mask' | float | int):
        return self.__mul__(self, other)

    def __sub__(self, other: 'Mask' | float | int):
        if isinstance(other, Mask):
            return DifferenceOfMasks(self, other)
        elif isinstance(other, (float, int)):
            return _AddedMask(self, -other)
        else:
            raise TypeError(f"Only masks and numbers can be substracted with masks, not {type(other)}")
    
    def __div__(self, other: 'Mask' | float | int):
        if other == 0:
            raise ZeroDivisionError()
        if isinstance(other, Mask):
            return DivisionOfMasks(self, other)
        elif isinstance(other, (float, int)):
            return _MultipliedMask(self, 1/other)
        else:
            raise TypeError(f"Only masks and numbers can divide masks, not {type(other)}")

    def __mod__(self, other: 'Mask' | float):
        if isinstance(other, Mask):
            return ModulusOfMasks(self, other)
        elif isinstance(other, float):
            return _ModulusedMask(self, other)
        else:
            raise TypeError(f"Only masks and numbers can be used as modulus for masks, not {type(other)}")

class UniformMask(Mask):
    """A Uniform mask is a mask filled with a unique value."""

    def __init__(self, value: float):
        super().__init__()
        self._value = value
    
    def _load(self, width, height, **ld_kwargs):
        self.matrix = np.full((width, height), np.clip(self._value, 0, 1))

class _OperationMask(Mask):

    def __init__(self, mask: Mask, value: float | int):
        self._mask = mask
        self._value = value

class _AddedMask(_OperationMask):

    def _load(self, width, height, **ld_kwargs):
        need_to_unload = False
        if not self._mask.is_loaded():
            need_to_unload = True
            self._mask.load(width, height, **ld_kwargs)
        self.matrix = np.clip(self._mask.matrix + self._value, 0, 1)
        if need_to_unload:
            self._mask.unload()

class _MultipliedMask(_OperationMask):

    def _load(self, width, height, **ld_kwargs):
        need_to_unload = False
        if not self._mask.is_loaded():
            need_to_unload = True
            self._mask.load(width, height, **ld_kwargs)
        self.matrix = np.clip(self._mask.matrix * self._value, 0, 1)
        if need_to_unload:
            self._mask.unload()

class _ModulusedMask(_OperationMask):

    def _load(self, width, height, **ld_kwargs):
        need_to_unload = False
        if not self._mask.is_loaded():
            need_to_unload = True
            self._mask.load(width, height, **ld_kwargs)
        self.matrix = np.mod(self._mask.matrix, self._value)
        if need_to_unload:
            self._mask.unload()

class MatrixMask(Mask):
    """
    A matrix mask is a mask based on a matrix, this matrix can be changed.
    When loaded or updated, the matrix of the mask is padded or cropped to fit the requested width and height.
    """

    def __init__(self, matrix: np.ndarray) -> None:
        """
        A matrix mask is a mask based on a matrix, this matrix can be changed.
        When loaded or updated, the matrix of the mask is padded or cropped to fit the requested width and height, and clipped in [0, 1]

        Params:
        - matrix: np.ndarray: the matrix on which the mask is based
        """

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
        """Update the current matrix with a user-defined matrix.
            The matrix is padded or cropeed to it the requested width and height.
        """
        self._matrix = new_matrix
        self._load(*self.matrix.shape)

class _MaskCombination(Mask, ABC):
    """MaskCombinations is an abstract class for all mask combinations: sum, products and average"""

    def __init__(self, *masks: Mask):
        """
        Combine the masks.

        Params:
        ---
        - *masks: Mask, the masks to be combined.
        """

        super().__init__()
        self.masks = masks

    @abstractmethod
    def _combine(self, *matrices: np.ndarray) -> np.ndarray:
        raise NotImplementedError()

    def _load(self, width:int, height: int, **ld_kwargs):
        for mask in self.masks:
            if not mask.is_loaded():
                mask.load(width, height, **ld_kwargs)

        self.matrix = self._combine(*(mask.matrix for mask in self.masks))

class SumOfMasks(_MaskCombination):
    """
    A sum of masks is a mask based on the sum of the matrixes of the masks, clamped between 0 and 1.
    For binary masks, it acts like union.
    """

    def _combine(self, *matrices):
        return np.clip(sum(matrices), 0, 1)

class DifferenceOfMasks(_MaskCombination):
    """
    A difference of masks is a mask based on the difference between the matrixes of two masks, clamped between 0 and 1.
    """
    # pylint: disable=arguments-differ
    def _combine(self, matrix1, matrix2):
        return matrix1 - matrix2

class DivisionOfMasks(_MaskCombination):
    """
    A division of masks is a mask based on the quotient between the matrixes of two masks, clamped between 0 and 1.
    Division by 0 are ignored and the value in the first matrix is kept.
    """
    # pylint: disable=arguments-differ
    def _combine(self, matrix1, matrix2):
        matrix2 = matrix2.copy()
        matrix2[matrix2 == 0] = 1
        return np.clip(np.divide(matrix1, matrix2), 0, 1)

class ModulusOfMasks(_MaskCombination):
    """
    A modulus of mask is mask based on the element-wise modulus of a matrix by another.
    """
    # pylint: disable=arguments-differ
    def _combine(self, matrix1, matrix2):
        return np.mod(matrix1, matrix2)   

class ProductOfMasks(_MaskCombination):
    """
    A product of masks is a mask based on the product of the matrixes of the masks.
    For binary masks, it acts like intersections.
    """

    def _combine(self, *matrices):
        prod = 1
        for mat in matrices:
            prod*=mat
        return prod
class AverageOfMasks(_MaskCombination):
    """
    An average of masks is a mask based on the average of the matrixes of the masks.
    """

    def __init__(self, *masks: Mask, weights: Sequence = None):
        """
        An average of masks is a mask based on the average of the matrixes of the masks.

        Params:
        ---
        - *masks: Mask, the masks to be averaged.
        - weights: Sequence, a sequence of number to be used to weight the average.

        Raises:
        ---
        ValueError if the weights are provded and do not have a length equa to the number of masks.
        """
        if weights is None:
            weights = [1]*len(masks)
        if len(weights) != len(masks):
            raise ValueError("The number of weights should match the number of masks")
        super().__init__(*masks)
        self.weights = weights

    def _combine(self, *matrices):
        avg = 0
        for matrix, weight in zip(matrices, self.weights):
            avg += matrix*weight

        avg /= sum(self.weights)
        return avg

class BlitMaskOnMask(_MaskCombination):
    """
    A blit mask on mask is a mask where the values of the background below (or above) a given threshold are replaced
    by the values on the foreground that are below a given threshold.
    """

    def __init__(self, background: Mask, foreground: Mask, bg_threshold: float = 0, fg_threshold: float = 0.5, reverse: bool = False):
        """
        Replace the values from a mask by others.
        
        Params:
        ---
        - background: mask, the mask having some values to be replaced.
        - foreground: mask, the mask whose values will replace the background values.
        - bg_threshold: Only the value of the background above (or below if reverse is True) that threshold are replaced.
        - fg_threshold: Only the value of the foreground below that threshold are used.
        - reverse: flag for comparison with bg_threshold.
        """
        super().__init__(background, foreground)
        self.bg_threshold = bg_threshold
        self.fg_threshold = fg_threshold
        self.reverse = reverse
    #pylint: disable=arguments-differ
    def _combine(self, background_matrix, foreground_matrix) -> np.ndarray:
        matrix = background_matrix
        if self.reverse:
            positions_to_keep = (background_matrix < self.bg_threshold) & (foreground_matrix < self.fg_threshold)
        else:
            positions_to_keep = (background_matrix > self.bg_threshold) & (foreground_matrix < self.fg_threshold)
        matrix[positions_to_keep] = foreground_matrix[positions_to_keep]
        return matrix
