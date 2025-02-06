"""The art class is the base for all the surfaces and animated surfaces of the game."""
from abc import ABC, abstractmethod
from threading import Thread
from pygame import Surface, image, surfarray as sa, Rect
from PIL import Image
from ..transform import Transformation, Pipeline, ExtractSlice, ExtractOne

class Art(ABC):
    """The art class is the base for all the surfaces and animated surfaces of the game."""

    def __init__(self, transformation: Transformation = None, force_load_on_start: bool = False, permanent: bool = False) -> None:
        super().__init__()
        self._surfaces: tuple[Surface] = ()
        self._durations: tuple[int] = ()
        self._introduction = 0
        self._loaded = False

        self._time_since_last_change = 0
        self._index = 0

        self._height = -1
        self._width = -1
        self._on_loading_transformation = transformation

        self._buffer_transfo_pipeline = Pipeline()

        self._force_load_on_start = force_load_on_start
        self._permanent = permanent
        self._transfo_thread = None
        self._has_changed = False
        self._copies: list[_ArtAsCopy] = []
        self._references: list[_ArtAsReference] = []
    
    @property
    def surfaces(self):
        return self._surfaces
    
    @property
    def durations(self):
        return self._durations
    
    @property
    def introduction(self):
        return self._introduction

    def set_load_on_start(self):
        """Set the force_load_start_attribute to be True."""
        self._force_load_on_start = True

    def start(self, **ld_kwargs):
        """Call this method at the start of the phase."""
        if self._force_load_on_start and not self._loaded:
            self.load(**ld_kwargs)

    def _find_initial_dimension(self):
        if self._on_loading_transformation:
            self._width, self._height = self._on_loading_transformation.get_new_dimension(self._width, self._height)

    def _verify_sizes(self):
        """verify that all surfaces have the same sizes."""
        heights = set(surf.get_height() for surf in self.surfaces)
        widths = set(surf.get_width() for surf in self.surfaces)
        if len(heights) != 1:
            raise ValueError(f"All images of the art does not have the same height, got\n{heights}")
        if len(widths) != 1:
            raise ValueError(f"All images of the art does not have the same width, got\n{widths}")

    @property
    def size(self):
        """Return the size of the art."""
        return (self.width, self._height)

    @property
    def height(self):
        """Return the height of the art."""
        return self._height

    @property
    def width(self):
        """Return the width of the art."""
        return self._width

    @property
    def is_loaded(self):
        """Return true if the art is loaded"""
        return self._loaded

    @property
    def total_duration(self):
        """Return the durations of the frames in the art."""
        if len(self.durations) > 1:
            return sum(self.durations)
        return 0

    @abstractmethod
    def _load(self, **ld_kwargs):
        raise NotImplementedError()

    @property
    def index(self):
        """Return the current index of the frame displayed."""
        return self._index

    def unload(self):
        """Unload the surfaces."""
        self.reset() # Reset the index.
        if not self._permanent:
            if self._transfo_thread is not None:
                # Wait for the transformation thread to stop to not get surfaces still loaded in memory.
                self._transfo_thread.join()
            self._surfaces = ()
            self._durations = ()
            self._loaded = False

    def load(self, **ld_kwargs):
        """Load the art at the beginning of the phase"""
        self._time_since_last_change = 0
        self._index = 0
        if not self._loaded:
            self._load(**ld_kwargs)
            self._verify_sizes()
            self._loaded = True
            if not self._on_loading_transformation is None:
                self._transform(self._on_loading_transformation, **ld_kwargs)

        for copy in self._copies:
            if not copy.is_loaded:
                copy.load(**ld_kwargs)

    def update(self, loop_duration: float) -> bool:
        """
        Update the instance animation.
        
        Return True if the index changed.
        """
        if len(self.surfaces) > 1:
            self._time_since_last_change += loop_duration
            if self._time_since_last_change >= self.durations[self._index]:
                self._time_since_last_change -= self.durations[self._index]
                self._index += 1
                # Loop
                if self._index == len(self.surfaces):
                    self._index = self.introduction
                # If the loop_duration is too long, we reset the time to 0.
                if self._time_since_last_change >= self.durations[self._index]:
                    self._time_since_last_change = 0

                self._has_changed = True
        has_changed = self._has_changed # This can be set to True if the a transformation has been a applied recently, or if the index changed.
        self._has_changed = False
        return has_changed 

    def reset(self):
        """Reset the animation."""
        self._index = 0
        self._time_since_last_change = 0

    def get(self,  match: 'Art' = None, **ld_kwargs):
        """
        Return the current Frame.
        
        - match: Art, if not None, the index will match the index of the other art to match, otherwise, use its own index
        """
        
        if not self._loaded: # Load the art
            self.load(**ld_kwargs)

        if (
            not self._buffer_transfo_pipeline.is_empty()
            and (self._transfo_thread is None or not self._transfo_thread.is_alive())
        ): # Apply a transformation only if the last thread is finished
            if self._buffer_transfo_pipeline.require_parallelization():
                args = self._buffer_transfo_pipeline.copy(), # On a separate thread, in this case the transformation may be visible later.
                self._buffer_transfo_pipeline.clear()
                self._transfo_thread = Thread(target=self._transform, args=args, kwargs=ld_kwargs)
                self._transfo_thread.start()
            else:
                self._transform(self._buffer_transfo_pipeline, **ld_kwargs) # Or directly on the main thread.
                self._buffer_transfo_pipeline.clear()

        index = self._index if match is None else match.index
        return self.surfaces[index].copy() # The current surface
    
    def transform(self, transformation: Transformation):
        """Apply a transformation to an Art."""
        self._buffer_transfo_pipeline.add_transformation(transformation)

    def _transform(self, transformation: Transformation, **ld_kwargs):
        """Apply a transformation"""
        if self._loaded:
            (   self._surfaces,
                self._durations,
                self._introduction,
                index,
                self._width,
                self._height
            ) = transformation.apply(
                self._surfaces,
                self._durations,
                self._introduction,
                self._index,
                self._width,
                self._height,
                **ld_kwargs
            )
            if index is not None:
                self._index = index
            self._buffer_transfo_pipeline.clear()
            self._has_changed = True
            for reference in self._references:
                reference._has_changed = True
        else:
            raise RuntimeError("A transformation have be called on an unloaded Art, please use the art's constructor to transform the initial art.")

    def copy(self, additional_transformation: Transformation = None, permanent: bool = False) -> '_ArtAsCopy':
        """
        Return an independant copy of the art.
        
        If force_load_on_start is set to True, the copy will be loaded at the start of the phase. Set it to true if 
        """
        copy = _ArtAsCopy(self, additional_transformation, permanent)
        self._copies.append(copy)
        return copy
    
    def reference(self):
        """
        Return a dependant copy of the art. This new object shares the surfaces and durations, any transformation applied to it will be applied
        to the original art (and vice versa). The animation, however, is independant.
        """
        reference = _ArtAsReference(self)
        self._references.append(reference)
        return reference

    def get_rect(self, x: int, y: int) -> Rect:
        """Create a pygame.Rect without masked based on this art."""
        return self.surfaces[0].get_rect().move(x,y)

    def save(self, path: str, index: int | slice = None):
        """Save the art as a gif or as an image."""
        if not self.is_loaded():
            raise RuntimeError("Cannot save an unloaded art.")
        if len(self.surfaces) == 1:
            image.save(self.surfaces[0], path)
        elif index is not None and isinstance(index, int):
            image.save(self.surfaces[index%len(self.surfaces)], path)
        else:
            surfaces = self.surfaces[index] if isinstance(index, slice) else self.surfaces
            durations = self.durations[index] if isinstance(index, slice) else self.durations
            pil_images = [Image.fromarray(sa.array3d(surf)) for surf in surfaces]
            pil_images[0].save(path, format='GIF', save_all=True, append_images = pil_images[1:], duration=durations)
    
    def __len__(self):
        return len(self._surfaces)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.copy(ExtractSlice(key))
        elif isinstance(key, int):
            return self.copy(ExtractOne(key))
        else:
            raise TypeError(f"Art indices must be integers or slices, not {type(key)}")

class _ArtAsCopy(Art):

    def __init__(self, original: Art, additional_transformation: Transformation, permanent: bool = False):
        super().__init__(additional_transformation, original._force_load_on_start, permanent)
        # The on load transformation has been removed because the transformation are executed during the loading of the original
        self._original = original
        self._height = self._original.height
        self._width = self._original.width
        self._find_initial_dimension()

    def _load(self, **ld_kwargs):
        if not self._original.is_loaded:
            self._original.load(**ld_kwargs)

        self._surfaces = tuple(surf.copy() for surf in self._original.surfaces)
        self._durations = self._original.durations
        self._introduction = self._original.introduction

class _ArtAsReference(Art):

    def __init__(self, original: Art):

        super().__init__(None, original._force_load_on_start, original._permanent)
        self._original = original
        self._height = self._original.height
        self._width = self._original.width    

    def _load(self, **ld_kwargs):
        if not self._original.is_loaded:
            self._original.load(**ld_kwargs)

    def _transform(self, transformation: Transformation, **ld_kwargs):
        self._original._transform(transformation, **ld_kwargs)

    @property
    def surfaces(self):
        return self._original.surfaces
    
    @property
    def durations(self):
        return self._original.durations
    
    @property
    def introduction(self):
        return self._original.introduction