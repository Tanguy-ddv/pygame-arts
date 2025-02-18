"""The effect module contains transformation consisting on applying effects"""
from typing import Callable
from pygame import Surface, surfarray as sa
import numpy as np
from pygamecv import saturate, desaturate, shift_hue, lighten, darken
from .transformation import Transformation
from ..mask import Mask

class SetAlpha(Transformation):
    """
    The set alpha transformation is used to change the value of the alpha channel.
    """

    def __init__(self, alpha: int = None, mask: Mask = None) -> None:
        """
        If alpha is specified, the SetAlpha transformation replace the alpha value of all the pixel by a new value.
        if mask is specified, the transformation replace the alpha value of all pixel by the value of the mask.
        Pixels that are transparent from the begining will not change.

        Params:
        ---
        - alpha: int, an integer between 0 and 255
        - mask: as gamarts.mask.Mask. One of two must be given.
        """
        super().__init__()

        if alpha is None and mask is None:
            raise ValueError("Both alpha and mask cannot be None.")
        self.alpha = alpha
        self.mask = mask

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is None:
            for surf in surfaces:
                surf.set_alpha(self.alpha)
        else:
            if not self.mask.is_loaded():
                self.mask.load(width, height, **ld_kwargs)
            for surf in surfaces:
                alpha_array = sa.pixels_alpha(surf)
                alpha_array[:] = (1 - self.mask.matrix)*255

        return surfaces, durations, introduction, None, width, height

    def cost(self, width: int, height: int, length: int, **ld_kwargs):
        if self.mask is None:
            return 0
        else:
            return width*height*length

class _MatrixTransformation(Transformation):
    """Matrix transformations are bases for all transformation transforming the matrix with an effect."""

    def __init__(self, mask: Mask | None = None):
        self.mask = mask

    def cost(self, width: int, height:int, length: int, **ld_kwargs):
        if self.mask is None or not self.mask.is_loaded():
            return width*height*length
        # If the mask is not loaded yet, every pixel of something (either the mask or the surfaces) would be impacted.
        # If the mask is already loaded, we get the smallest submask.
        not_null_columns = self.mask.not_null_columns()
        not_null_rows = self.mask.not_null_rows()
        if not_null_columns and not_null_rows:
            return (not_null_columns[-1] - not_null_columns[0])*(not_null_rows[-1]*not_null_rows[0])*length
        return 0

class RBGMap(_MatrixTransformation):
    """
    An RGBMap is a transformation applied directly on the pixel of the surfaces. The alpha value is not taken into account.
    the function must be vectorized. (check numpy.vectorize)
    """

    def __init__(self, function: Callable[[int, int, int], tuple[int, int, int]], mask: Mask = None, mask_threshold: float = 0.99) -> None:
        """
        An RGBMap applies a pixel-by-pixel transformation.

        Params:
        ---
        - function: r,g,b -> (r,g,b). The mapping function.
        - mask: gamarts.mask.Mask, a mask. It is used to know what 
        - mask_threshold: float. The threshold with which the values in the mask is compared. If it is above, then the pixel is
        mapped to a new value. If it is below, the pixel stays unchanged.
        """
        super().__init__(mask)
        self.function = function
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip(np.apply_along_axis(lambda t: self.function(*t), 2, rgb_array), 0, 255).astype(np.int8)
            else:
                self.mask.load(width, height, **ld_kwargs)
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(np.apply_along_axis(lambda t: self.function(*t), 2, rgb_array[self.mask.matrix > self.mask_threshold]), 0, 255).astype(np.int8)

        return surfaces, durations, introduction, None, width, height

class RGBAMap(_MatrixTransformation):
    """
    An RGBAMap is a transformation applied directly on the pixel of the surfaces. The alpha value is taken into account.
    the function must be vectorized. (check numpy.vectorize)
    """

    def __init__(self, function: Callable[[int, int, int, int], tuple[int, int, int, int]], mask: Mask = None, mask_threshold: float = 0.99) -> None:
        """
        An RGBMap applies a pixel-by-pixel transformation.

        Params:
        ---
        - function: r,g,b,a -> (r,g,b,a). The mapping function.
        - mask: gamarts.mask.Mask, a mask. It is used to know what 
        - mask_threshold: float. The threshold with which the values in the mask is compared. If it is above, then the pixel is
        mapped to a new value. If it is below, the pixel stays unchanged.
        """
        super().__init__(mask)
        self.function = function
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):

        for surf in surfaces:

            if self.mask is None:
                rgb_array = sa.pixels3d(surf)
                alpha_array = sa.pixels_alpha(surf)
                r, g, b = rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2]
                new_r, new_g, new_b, new_a = self.function(r, g, b, alpha_array)
                rgb_array[:, :, 0] = new_r
                rgb_array[:, :, 1] = new_g
                rgb_array[:, :, 2] = new_b
                alpha_array[:] = new_a
            else:
                self.mask.load(width, height, **ld_kwargs)
                mask = self.mask.matrix > self.mask_threshold
                rgb_array = sa.pixels3d(surf)
                alpha_array = sa.pixels_alpha(surf)[mask]
                r, g, b = rgb_array[:, :, 0][mask], rgb_array[:, :, 1][mask], rgb_array[:, :, 2][mask]
                new_r, new_g, new_b, new_a = self.function(r, g, b, alpha_array)
                rgb_array[:, :, 0][mask] = new_r
                rgb_array[:, :, 1][mask] = new_g
                rgb_array[:, :, 2][mask] = new_b
                alpha_array[:] = new_a

        return surfaces, durations, introduction, None, width, height

class Saturate(_MatrixTransformation):
    """Saturate the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None) -> None:
        """
        Saturate the frames of the art by a given factor.

        Params:
        ---
        - factor: float, 0 <= factor <= 1. The factor by which the frames will be saturated.
        - mask: mask.Mask. If given, the saturation factor applied is mask.matrix*factor. The pixels will be saturated one by one.
        """
        super().__init__(mask)
        self.factor = factor

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is not None:
            self.mask.load(width, height, **ld_kwargs)
            factor = self.mask.matrix*self.factor
        else:
            factor = self.factor
        for surf in surfaces:
            saturate(surf, factor)

        return surfaces, durations, introduction, None, width, height
    
class Desaturate(_MatrixTransformation):
    """Desaturate the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None) -> None:
        """
        Desaturate the frames of the art by a given factor.

        Params:
        ---
        - factor: float, 0 <= factor <= 1. The factor by which the frames will be desaturated.
        - mask: mask.Mask. If given, the desaturation factor applied is mask.matrix*factor. The pixels will be desaturated one by one.
        """
        super().__init__(mask)
        self.factor = factor

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is not None:
            self.mask.load(width, height, **ld_kwargs)
            factor = self.mask.matrix*self.factor
        else:
            factor = self.factor
        for surf in surfaces:
            desaturate(surf, factor)

        return surfaces, durations, introduction, None, width, height
    
class Darken(_MatrixTransformation):
    """Darken the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None) -> None:
        """
        Darken the frames of the art by a given factor.

        Params:
        ---
        - factor: float, 0 <= factor <= 1. The factor by which the frames will be darkened.
        - mask: mask.Mask. If given, the darkening factor applied is mask.matrix*factor. The pixels will be darkened one by one.
        """
        super().__init__(mask)
        self.factor = factor

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is not None:
            self.mask.load(width, height, **ld_kwargs)
            factor = self.mask.matrix*self.factor
        else:
            factor = self.factor
        for surf in surfaces:
            darken(surf, factor)

        return surfaces, durations, introduction, None, width, height

class Lighten(_MatrixTransformation):
    """Lighten the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None) -> None:
        """
        Lighten the frames of the art by a given factor.

        Params:
        ---
        - factor: float, 0 <= factor <= 1. The factor by which the frames will be lightened.
        - mask: mask.Mask. If given, the lightening factor applied is mask.matrix*factor. The pixels will be lightened one by one.
        """
        super().__init__(mask)
        self.factor = factor

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is not None:
            self.mask.load(width, height, **ld_kwargs)
            factor = self.mask.matrix*self.factor
        else:
            factor = self.factor
        for surf in surfaces:
            lighten(surf, factor)

        return surfaces, durations, introduction, None, width, height

class ShiftHue(_MatrixTransformation):
    """Shift the hue of all surface of the art by a given value."""

    def __init__(self, value: int, mask: Mask = None) -> None:
        """
        shirt of the hue of the frames of the art by a given value.

        Params:
        ---
        - value: int. The value by which the hue will be shifted.
        - mask: mask.Mask. If given, the shifting value applied is mask.matrix*value. The pixels will be shifted one by one.
        """
        super().__init__(mask)
        self.value = value

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        if self.mask is not None:
            self.mask.load(width, height, **ld_kwargs)
            value = self.mask.matrix*self.value
        else:
            value = self.value
        for surf in surfaces:
            shift_hue(surf, value/2)

        return surfaces, durations, introduction, None, width, height

class Invert(_MatrixTransformation):
    """Invert the color of the art."""

    def __init__(self, mask: Mask = None, mask_threshold: float = 0.99):
        """
        Invert the color of the art.
        
        Params:
        ----
        - mask: mask.Mask. If specified, the mask is used to know what pixels are to be inverted.
        - mask_threshold: float. the threshold used to convert the mask into a boolean mask. Pixels whose value in the mask
        is above the threshold will be inverted. The other won't.
        """
        super().__init__(mask)
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = 255 - rgb_array
            else:
                self.mask.load(width, height, **ld_kwargs)
                rgb_array[self.mask.matrix > self.mask_threshold] = 255 - rgb_array[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, None, width, height

class AdjustContrast(_MatrixTransformation):
    """Change the contrast of an art. The constrast is a value between -255 and +255."""

    def __init__(self, contrast: int, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        """
        Change the contrast of an art. The constrast is a value between -255 and +255

        Params:
        ----
        - mask: mask.Mask. If specified, the mask is used to know what pixels are to be adjusted.
        - mask_threshold: float. the threshold used to convert the mask into a boolean mask. Pixels whose value in the mask
        is above the threshold will be adjusted. The other won't.
        """
        
        super().__init__(mask)
        self.factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip((self.factor * (rgb_array - 128) + 128).astype(np.int8), 0, 255)
            else:
                self.mask.load(width, height, **ld_kwargs)
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(
                    (self.factor * (rgb_array[self.mask.matrix > self.mask_threshold] - 128) + 128).astype(np.int8), 0, 255)

        return surfaces, durations, introduction, None, width, height

class AddBrightness(_MatrixTransformation):
    """Change the brightness of an art. The brightness is a value between -255 and +255."""

    def __init__(self, brightness: int, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        """
        Change the brightness of an art. The brightness is a value between -255 and +255.
        Adding brightness to the art will just add a fixed value to all the pixels.
        It is equivalent to use a RGBAMap with the function lambda r,g,b : (r+B, g+B, b+B) where B is the brightness.

        Params:
        ----
        - mask: mask.Mask. If specified, the mask is used to know what pixels are to be adjusted.
        - mask_threshold: float. the threshold used to convert the mask into a boolean mask. Pixels whose value in the mask
        is above the threshold will be adjusted. The other won't.
        """
        super().__init__(mask)
        self.brightness = np.int8(brightness)
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip(rgb_array + self.brightness, 0, 255).astype(np.int8)
            else:
                if not self.mask.is_loaded():
                    self.mask.load(width, height, **ld_kwargs)
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(rgb_array[self.mask.matrix > self.mask_threshold] + self.brightness, 0, 255)
        return surfaces, durations, introduction, None, width, height

class Gamma(_MatrixTransformation):
    """
    The gamma transformation is used to modify the brightness of the image.
    For 0 < gamma < 1, the dark pixels will be brighter and the bright pixels will not change
    For gamma > 1, the light pixels will be darker and the dark pixel will not change
    """

    def __init__(self, gamma: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        """
        Apply a gamma transformation.

        Params:
        ----
        - gamma: the parameter of the transformation.
        - mask: mask.Mask. If specified, the mask is used to know what pixels are to be adjusted.
        - mask_threshold: float. the threshold used to convert the mask into a boolean mask. Pixels whose value in the mask
        is above the threshold will be adjusted. The other won't.
        """
        super().__init__(mask)
        self.gamma = gamma
        self.mask_threshold = mask_threshold  

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, **ld_kwargs):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip(((rgb_array/255)**self.gamma * 255).astype(np.int8), 0, 255)
            else:
                if not self.mask.is_loaded():
                    self.mask.load(width, height, **ld_kwargs)
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(
                    ((rgb_array[self.mask.matrix > self.mask_threshold]/255)**self.gamma * 255).astype(np.int8), 0, 255)

        return surfaces, durations, introduction, None, width, height
