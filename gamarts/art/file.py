"""The file module contains classes to open images, gifs and folders as arts."""
from typing import Iterable
import os
from PIL import Image
from pygame.image import load, fromstring
from .art import Art
from .._error import LoadingError
from ..transform import Transformation

class ImageFile(Art):
    """
    The ImageFile class is an Art loaded from an image.
    Accepted format are: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm

    Example:
    ---
    - ``ImageFile("my_image.png")`` is an Art displaying the image stored at "my_image.png"
    - ``ImageFile("characters/char1.jpeg", False)`` will load an the image stored at "characyers/char1.jpeg" and convert it in the RGB format
    """

    def __init__(self, file: str, transparency: bool = True, transformation: Transformation = None) -> None:
        """
        The ImageFile class is an Art loaded from an image.
        Accepted format are: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
        
        Params:
        ----
        - file: str, the path to the file.
        - transparency: bool = True, whether the surface has some transparency. ImageFile with transparency are in the RGBA format, while ImageFiles
        without are in the RGB format (without alpha channel).
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        """
        super().__init__(transformation)
        self.full_path = file
        im = Image.open(self.full_path)
        self._width, self._height = im.size
        self._transparency = transparency
        im.close()
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        if self._transparency: self._surfaces = (load(self.full_path).convert_alpha(),)
        else: self._surfaces = (load(self.full_path).convert(),)
        self._durations = (0,)

class ImageFolder(Art):
    """
    The ImageFolder class is an Art loaded from multiple images in a folder.
    All image must have one of these formats: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
    The animation is reconstructed by taking images in the alphabetical order from the file. All images must have the same sizes
    
    Example:
    -----
    - ``ImageFolder("my_images/", [100, 200, 100])``
    is an Art displaying the images stored in the folder "assets/images/my_images/".
    The folder contains 3 images and the animation will be 400 ms, 100 ms for the first image, 200 ms for the second, and 100 for the last
    - ``ImageFolder("characters/char1/running/", 70)`` is an Art displaying the images stored in the folder "assets/images/characters/char1/running/".
    Every images in the folder will be display 70 ms.
    - ``ImageFolder("my_images/", 70, 5)`` is an Art displaying the images stored in the folder "assets/images/my_images/".
    The folder must contains at least 5 images.
    When all the images have been displayed, it does not loop on the very first but on the 6th.
    Frame will be displayed in the following order, if there are 9 frames:
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 5, 6, 7, 8, 5, 6, 7, 8, 5, 6, ...].
    """

    def __init__(
        self,
        folder: str,
        durations: Iterable[int] | int,
        introduction: int = 0,
        transformation: Transformation = None,
    ) -> None:
        """
        The ImageFolder class is an Art loaded from multiple images in a folder.
        All image must have one of these formats: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
        The animation is reconstructed by taking images in the alphabetical order from the file. All images must have the same sizes.

        Params:
        ---
        - folder: str, the path to the folder.
        - durations: Iterable[int] | int, the duration(s) of the frames. If an iterable is provided, it must have the same number of elements than
        the number of images in the folder.
        - introduction: the introduction of the art. If specified, the art will not display the first frame after the last but this one instead. See examples.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        
        Raises:
        ---
        - LoadingError if the specified introduction is larger than the number of images in the folder.
        - LoadingError if the iterable of durations does not have the same length as the number of images in the folder.
        """
        super().__init__(transformation)
        self.full_path = folder
        self.durs = durations
        self._introduction = introduction

        self._paths = [
            os.path.join(self.full_path, f)
            for f in os.listdir(self.full_path)
            if os.path.isfile(os.path.join(self.full_path, f))
        ]
        im = Image.open(self._paths[0])
        self._width, self._height = im.size
        im.close()
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        self._surfaces = tuple(load(path) for path in self._paths)
        if self._introduction > len(self._paths):
            raise LoadingError(
                f"The introduction specified for this ImageFolder is too high, got {self._introduction} while there is only {len(self.surfaces)} images."
            )
        if isinstance(self.durs, int):
            self._durations = tuple(self.durs for _ in self._paths)
        else:
            if len(self.durs) != len(self._paths):
                raise LoadingError(
                    f"The length of the durations list ({len(self.durs)}) does not match the len of the number of images ({len(self.surfaces)})"
                )
            self._durations = tuple(self.durs)
        self._verify_sizes()

class GIFFile(Art):
    """
    The GIFFile is an Art that displays a gif.
    
    Example:
    -----
    - GIFFile("my_animation.gif") is an Art displaying the gif stored at "assets/images/my_animation.gif".
    - GIFFile("my_animation.gif", 10) is an Art displaying the gif stored at "assets/images/my_animation.gif".
    it must have at least 10 images.
    When all the images have been displayed, do not loop on the very first but on the 10th.
    """

    def __init__(self, file: str, introduction: int = 0, transformation: Transformation = None) -> None:
        """
        The GIFFile is an Art that displays a gif.

        Params:
        ----
        - file: str, the path to the .gif file.
        - introduction: the introduction of the art. If specified, the art will not display the first frame after the last but this one instead. See examples.
        - transformation: transform.Transformation = None. Any transformation (or Pipeline) that will be applied to the art when it is loaded.
        
        Raises:
        ---
        - LoadingError if the specified introduction is larger than the number of images in the folder.
        """
        super().__init__(transformation)
        self.full_path = file
        self._introduction = introduction
        im = Image.open(self.full_path)
        self._width, self._height = im.size
        im.close()
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        gif = Image.open(self.full_path)
        gif.seek(0)
        images = [fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA')]
        image_durations = [gif.info['duration']]
        while True:
            try:
                gif.seek(gif.tell()+1)
                images.append(fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA'))
                image_durations.append(gif.info['duration'])
            except EOFError:
                break
        self._surfaces = tuple(images)
        self._durations = tuple(image_durations)

        if self._introduction > len(self.surfaces):
            raise LoadingError(
                f"The introduction specified for this GIFFile is too high, got {self._introduction} while there is only {len(self.surfaces)} images."
            )
        gif.close()
