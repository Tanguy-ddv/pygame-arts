# Gamarts

Gamarts is a python library providing a unique way to represent static and animated surfaces in pygame, alongside with a clever loading and unloading behavior.
Gamarts provides one class, ``Art`` as an abstract class for multiple classes representing animated objects or geometries. Gamarts also provides transformation
and drawing capabilities for these arts.

## gamarts.Art

### General usage

The ``Art`` class is the main object of the library. Arts replace the ``Surface`` from pygame. They are basically a list of Surfaces, but implements also durations, as well as update, get, start, load and unload method to correctly manage the art. Transformation can be applied on an Art by using the gamarts.transform module.
All Arts have some common behavior, and only differ in their loading method. Some Arts will load images from a file while other are drawing. Some are even both.
However, they all share common patterns and have initialization argument in common. An example for creating and using an ``Art`` is shown below.

```python
from gamarts import ImageFile # An art with one surface loaded from a file.
from gamarts.transform import ShiftHue
import pygame
lenna = ImageFile("images/Lenna.png", force_load_on_start = True, permanent = False)
pygame.init()
screen = pygame.display.set_mode(*lenna.size) # even if the image isn't loaded, its size is available.
# Now, lenna has not been loaded yet
lenna.start() # Load lenna if force_load_on_start is True.
# Used for arts that cannot be loaded in the mainloop
clock = pygame.time.Clock()
# these loading kwargs are essential and should be passed to the get method given later.
# the values can be changed, if you create your own arts with different loading kwargs,
# you can safely add it to the dict.
ld_kwargs = {'antialias' : True, 'cost_threshold' : 100_000}
FPS=60
running = True
while running:
    loop_duration = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            lenna.transform(ShiftHue(50)) # If we press the space key, we shift the hue of the of the Art by 50°.
            # This is a pending transformation that will happen only at the next .get()
    
    lenna.update(loop_duration) # Update the art. For arts with several surfaces, otherwise it doesn't do anything
    surf = lenna.get(**ld_kwargs) # get the current surface of the art. At this point, if the art have not been loaded, load it (only once of course)
    # The pending transformation is also applied now.
    screen.blit(surf, (0, 0))
    pygame.display.flip()

lenna.unload() # Unload the Art if permanent is False.
pygame.quit()
```

### Common elements

All arts have several methods and properties:
- ``surfaces``: a property returning a tuple of all the art's surfaces
- ``durations``: a property returning a tuple of the duration of each frame in the animation
- ``introduction``: a property returning the introduction of the art.
- ``size``, ``height`` and ``width``: properties, used to get the dimension of the art.
- ``is_loaded``: a property returning whether the art is loaded.
- ``total_duration``: a property returning the total duration of an animation, from the first to last frame
- ``index``: a property returning the index-th frame of the animation that is currently displayed.
- ``transform()``: is used to apply a transformation to an Art, see below
- ``get_rect()``: returns a rect generated with the Art
- ``save(index: int = None)``: saves the Art as a GIF or as an image, if the index is provided and the art has more than 1 surface
- ``reset()`` resets the animation to the first frame.
- ``update(loop_duration)`` updates the index of the frame based on time and their durations. It will return True if the art changed since the last call (a transformation or a new frame is to be shown.)
- ``get(match: Art, **ld_kwargs) -> Surface`` returns the current surface of the animation, and apply the transformations waiting to be applied.
- ``copy(additional_transformation: Transformation) -> Art``, return a fully indendent art using the frame of the original as initial
surfaces, they can be further transformed.
- ``reference() -> Art`` returns a dependant art. The original and the reference will fully share their surfaces, durations and introduction, any tranformation on one
will happen on the other, however, they have independant indices.
- ``load(**ld_kwargs)`` loads the art. It is called automatically at the first call of ``get`` if the art has not been loaded yet.
- ``unload()`` unload the art to release some memory.

- ``len(art)`` returns the number of frames in the animation
- ``art[x]`` where x is any slice or int (for example, ``art[1:9:3]``) returns a copy with a subset of the arts.

If the surface obtain with ``.get()`` is modified later, the modification will appear only on this surface. ``.get`` has another argument, match: gamarts.Art, used to match the index of another art to synchronize animations. The constructor of each Art also has another argument, transformation: gamarts.transform.Transformation, used to apply a transformation in the loading of the Art. All Arts have a list of durations representing the time each frame will be displayed. They also can have an introduction, being the number of frames that it skipped when the animation loops. For example, an animation of a character running could be composed of 3 frames to prepare and 7 to run. If introduction=3, then the 8th displayed frame is the animation's fourth.

### All arts

To create one of the many Art gamarts allows to create, you have to instanciante an instance of one of the subclasses:

- ``ImageFile(path)`` creates an Art based on one surface, loaded in pygame as any other image.
- ``ImageFolder(path, durations)`` creates an animation based on all the images saved on one folder. All images must have the exact same dimensions. The durations must be specified and an introduction argument can also be given. Frames are loaded by alphabetical order.
- ``GIFFile(path)`` creates an Art based on all the frames of a .gif animated file. The durations are also already specified in the file, you can however set the introduction.

For the following arts, the entry 'antialias' of the ld_kwargs dict is used to specify whether antialiasing should be used or not. An optional argument, ``background_color`` can be used to specify the color of the background the Art are shown on, improving the result of using antialiasing. Antialiasing can be disabled for them by setting the optional argument ``allow_antialias`` to False.

- ``Rectange(color, width, height, thickness)`` creates a rectangle. Thickness is the width argument of pygame drawings.
- ``RoundedRectangle(color, width, height, top_left, top_right, bottom_left, bottom_right, thickness)`` create a rectangle with rounded corners Thickness is the width argument of pygame drawings.
- ``Circle(color, radius, thickness)`` creates a circle. Thickness is the width argument of pygame drawings.
- ``Ellipse(color, horizontal_radius, vertcal_radius, thickness)`` creates an ellipse. Thickness is the width argument of pygame drawings.
- ``Polygon(color, points, thickness)`` creates a polygon defined by the points. Thickness is the width argument of pygame drawings.

The following arts are textures, they are Arts drawn inside of a geometry. They have the same durations and introduction than the texture argument of the constructor.

- ``TexturedPolygon(texture, points)`` creates a polygon filled with the texture.
- ``TexturedEllipse(texture, horizontal_radius, vertical_radius, center)``creates an Ellipse filled with the texture.
- ``TexturedRoundedRectangle(texture, top_left, top_right, bottom_left, bottom_right)``creates a rounded rectangle filled with the texture, with the same width and height.
- ``TexturedCircle(texture, radius, center, draw_top_right, draw_top_left, draw_bottom_right, draw_bottom_left)`` creates a circle filled with the texture. If any of the draw... argument is set to False, the corresponding quarter of circle is not drawn.

All of the Art have an optional argument ``transformation`` that performs a transformation on the Art during its loading. transformation can also be applied during the game loop. They are explained below.

## gamarts.transform

### Transformations

Multiple transformations are available to transform an Ar, they can be called by created a instance of one of the subclasses of ``Transformation``, listed below, and given as argument to the .transform() method of an art or in its constructor. If multiple transformations need to be applied, they have to be put inside a ``Pipeline``. Transformations can be created at the beginning of the game and assigned to a variable, or during the loop.

- Transformations of the size of the art:
    - ``Rotate(angle)`` rotates all the surfaces of the art like ``pygame.transform.rotate``.
    - ``Zoom(scale, smooth)`` rescales all the surfaces of the art like ``pygame.transform.scale_by``.
    - ``Resize(size, smooth)`` resizes all the surfaces of the  art like ``pygame.transform.scale``.
    - ``Crop(left, top, width, height)`` crops all the surfaces of the art.
    - ``Pad(color, left, right, top, bottom)`` adds padding to all the surfaces of the art.
    - ``Flip(horizontal, vertical)`` flips all the surfaces of the art ``like pygame.transform.flip``.
    - ``Transpose`` performs a matrix-like transposition of  the surfaces of the art.
    - ``VerticalChop`` removes a vertical band in all the surfaces of the art.
    - ``HorizontalChop`` removes a horizontal band in all the surfaces of the art.

- Transformation of the durations, current index or introduction of the art:
    - ``SpeedUp(scale)`` divides all the durations by the scale.
    - ``SlowDown(scale)`` multiplies all the durations by the scale.
    - ``SetDuration(new_duration)`` sets all the durations of the frame to this duration.
    - ``SetDurations(new_durations)`` sets the durations of the frame with a new list of durations. Must have the same length than the current number of frames.
    - ``SetIntroductionIndex(introduction)`` sets the introduction attribute based on the provided index.
    - ``SetIntroductionTime(introduction)`` sets the introduction to an index corresponding to the frame displayed at the given time.
    - ``RandomizeIndex()`` randomizes the current index.
    - ``Shuffle()`` shuffles the frames.

- Transformations that extracts a subanimation from an animation
    - ``ExtractSlice(slice)`` extracts a subset of the frames with the index slices. If some of the indices from the slice are greater than the number of frames, the extraction continues starting from the introduction.
    - ``ExtractOne(index)`` extracts one frame from the art.
    - ``First()`` extracts the first frame.
    - ``Last()`` extracts the last frame.
    - ``ExtractTime(time)`` extracts the frame displayed at a given time.
    - ``ExtractWindow(from_time, to_time)`` extracts an animation from one time to another.

- Transformation that draws on the art. All of these transformation uses the 'antialias' entry from the ld_kwargs to draw with or without antialias. The optional argument ``allow_antialias`` can also be set to False in order to disable the usage of antialias. Gamarts uses the [pygameCV](https://pygamecv.readthedocs.io/en/latest/) library for all the drawings to improve the drawing capacities of pygame. The thickness argument represent the thickness of the line used to draw anything on the surfaces. If the thickness is 0, the geometry will be filled. Otherwise, the line will overflow halfly on the inside of the draw, and halfly on the outside. For example, a circle with a thickness of 10 will be a filled from radius - 5 to radius + 5.
    - ``DrawCircle(color, radius, center, thickness)`` draws a circle on all surfaces of the art.
    - ``DrawRectangle(color, rect, thickness)`` draws a rectangle on all surfaces of the art.
    - ``DrawRoundedRectantle(color, rect, top_left, top_right, top_right, bottom_right, bottom_left, thickness)`` draws a rounded rectangle on all surfaces of the art.
    - ``DrawEllipse(color, x_radius, y_radius, center, thickness, angle)`` draws a rotated ellipse on all surfaces of the art.
    - ``DrawPolygon(color, points, thickness)`` draws a polygon on all surfaces of the art.
    - ``DrawLine(color, p1, p2, thickness)`` draws a line on all surfaces of the art.
    - ``DrawLines(color, points, thickness, closed)`` draws multiple lines on all the surfaces of an art. This is faster than calling multiple times DrawLine.
    - ``DrawArc(color, ellipsis_center, horizontal_radius, vertical_radius, from_angle, to_angle, angle, thickness)`` draws an arc from an rotated ellipsis. The arc is draw counterclockwise.
    - ``DrawPie(color, ellipsis_center, horizontal_radius, vertical_radius, from_angle, to_angle, angle, thickness)`` draws an arc from an rotated ellipsis. The arc is draw counterclockwise. The arc is linked to the center of the ellipsis.

- Transformations that applies an effect on an art, they can be called with a mask. In this case, the factor multiplies a matrix (generated by the mask) of floats between 0 and 1 and is used to as a per-pixel factor.
    - ``SetAlpha(alpha, mask)`` sets the alpha of an art. If a mask is given, set the alpha value of each pixel to alpha*mask.matrix
    - ``GrayScale()`` converts all the frames of an art into a gray scale with ``pygame.transform.gray_scale``.
    - ``RBGMap(func)`` applies a transformation of all pixels one by one.
    - ``RGBAMap`(func)`` applies a transformation of all pixels and its alpha value.
    - ``Saturate(factor)`` applies a saturation effect.
    - ``Desaturation(factor)`` applies a desaturation effect (colors becomes more gray).
    - ``Darken(factor)`` reduces the luminosity.
    - ``Lighten(factor)`` increases the luminosity.
    - ``ShiftHue(value)`` shifts the value of the hue.
    - ``AdjustContrast(constrast)`` changes the contrast.
    - ``AddBrightness(value)`` modifies the brightness.
    - ``Gamma(gamma)`` applies a gamma transformation

### Masks

A few masks are implemented inside the gamarts.mask module. The list of masks is listed below:

- ``MatrixMask(matrix)`` is a mask directly based on a matrix. The matrix should contains floats between 0 and 1
- ``Circle(radius, center)`` is a binary masks. The corresponding matrix has 0 inside the circle and 1 outside.
- ``Ellipse(radius_x, radius_y, center)`` is a binary masks. The corresponding matrix has 0 inside the ellipse and 1 outside.
- ``Rectangle(left, top, right, bottom)`` is a binary masks. The corresponding matrix has 0 inisde the rectangle and 0 outside.
- ``Polygon(points)`` is a binary mask. The corresponding matrix has 0 inside the  polygon and 1 outside. They are based on pygame's polygon.
- ``RoundedRectangle(left, top, right, bottom, radius)`` is a binary mask. The corresponding matrix has 0 inisde the rounded rectangle and 1 outside. All corners have the same angle.
- ``GradientCircle(inner_radius, outer_radius, transition, center)`` is a continuous mask. The corresponding matrix has 0 inside the inner cirlce, 1 outside the outer circle and a value in-between when inside the outer circle but inside the inner circle
- ``GradientRectangle(inner_left, inner_top, inner_right, inner_bottom, outer_left, outer_top, outer_right, outer_bottom)`` is a continuous mask. the corresponding matrix has 0 inside the inner rectangle, 0 outside the outer rectangle, and a velue-between when inside the outer rectangle but outside the inner rectangle.

### Cost

Each transformation has a cost. This cost is calculated by the cost method and represent how long a transformation can be. It mainly depends on the number of pixels that have to be copied, which depends on the size of the drawing or mask for an effect. If the cost is higher than a given threshold (the ``cost_threshold`` entry of the ld_kwargs), then the transformation is computed in an independant thread.

## Contributing

Any contribution to help improving gamarts is welcome. New arts, transformations or masks can be added. Optimization and bug reporting are of course accepted!

## License

Gamarts is distributed under a GNU General Public License.