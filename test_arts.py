import pygame

def init():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    return screen

def loop(func, screen):
    running = True
    clock = pygame.time.Clock()
    while running:
        loop_duration = clock.tick(100)
        im = func(loop_duration)
        screen.blit(im, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()


# Test arts from files

def update_and_show(loop_duration, art):
    art.update(loop_duration)
    return art.get()

def see_image_no_alpha():
    from gamarts import ImageFile
    screen = init()
    lenna = ImageFile("images/Lenna.png")
    loop(lambda loop_duration: update_and_show(loop_duration, lenna), screen)

def see_image_alpha():
    from gamarts import ImageFile
    screen = init()
    lenna = ImageFile("images/Lenna_alpha.png")
    loop(lambda loop_duration: update_and_show(loop_duration, lenna), screen)

def see_gif():
    from gamarts import GIFFile
    screen = init()
    earth = GIFFile("images/wikipedia_earth.gif")
    loop(lambda loop_duration: update_and_show(loop_duration, earth), screen)
    
def see_folder():
    from gamarts import ImageFolder
    screen = init()
    squares = ImageFolder("images/squares", 700)
    loop(lambda loop_duration: update_and_show(loop_duration, squares), screen)

# see_image_no_alpha()
# see_image_alpha()
# see_gif()
# see_folder()


# -- Test geometries

def update_and_show(loop_duration, arts, antialias):
    for art in arts:
        art.update(loop_duration)
    surf = pygame.Surface((800, 600), pygame.SRCALPHA)
    pos = [(0, 0), (200, 200), (200, 0), (0, 200), (400, 0), (400, 200), (400, 400), (200, 400), (0, 400)]
    for art, p in zip(arts, pos):
        surf.blit(art.get(antialias=antialias), p)
    return surf

def see_geometries():
    from gamarts import Rectangle, RoundedRectangle, Circle, Art
    screen = init()
    screen.fill((0, 0, 0, 255))
    pygame.draw.line(screen, (255, 255, 255), (0, 200), (800, 200))
    pygame.draw.line(screen, (255, 255, 255), (0, 400), (800, 400))
    pygame.draw.line(screen, (255, 255, 255), (200, 0), (200, 600))
    pygame.draw.line(screen, (255, 255, 255), (400, 0), (400, 600))


    arts: list[Art] = [
        Rectangle((100, 100, 0), 150, 150, 10),
        Rectangle((200, 255, 0), 150, 100, 0),
        RoundedRectangle(pygame.Color(255, 0, 0), 150, 150, 50, thickness=30),
        RoundedRectangle(pygame.Color(0, 255, 0), 150, 150, 30, thickness=30, allow_antialias=False),
        RoundedRectangle((0, 0, 255), 150, 150, top_left=150, top_right=0, bottom_left=0, bottom_right=150),
        RoundedRectangle((0, 0, 100), 150, 150, top_left=10, top_right=60, bottom_left=0, bottom_right=80),
        Circle((255, 255, 0), 75, 10),
        Circle((0, 255, 255), 75, 20, allow_antialias=False),
        Circle((255, 0, 255), 75, 20),
    ]
    
    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_geometries2():
    from gamarts import Ellipse, Polygon, Art
    screen = init()
    screen.fill((0, 0, 0, 255))
    pygame.draw.line(screen, (255, 255, 255), (0, 200), (800, 200))
    pygame.draw.line(screen, (255, 255, 255), (0, 400), (800, 400))
    pygame.draw.line(screen, (255, 255, 255), (200, 0), (200, 600))
    pygame.draw.line(screen, (255, 255, 255), (400, 0), (400, 600))


    arts: list[Art] = [
        Ellipse((255, 0, 0, 255), 75, 75, 10),
        Ellipse((255, 255, 255, 255), 50, 75, 10),
        Ellipse((255, 255, 0, 255), 50, 75, 70),
        Ellipse((0, 255, 0, 255), 50, 75, 0),
        Polygon((255, 0, 0), [(0, 0), (100, 100), (0, 100)]),
        Polygon((0, 0, 255), [(100, 100), (10, 10), (0, 100)], 10),
        Polygon((0, 255, 0), [(-100, -100), (0, 0), (0, -100)]),
        Polygon((100, 100, 255), [(0, 0), (100, 100), (0, 100), (100, 0)]),
        Polygon((100, 255, 100), [(0, 0), (100, 100), (0, 100), (100, 0)], thickness=20)
    ]
    
    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_textures():
    from gamarts import GIFFile, TexturedCircle, TexturedEllipse, TexturedPolygon, TexturedRoundedRectangle, Art
    screen = init()
    screen.fill((255, 255, 255, 255))
    earth = GIFFile("images/wikipedia_earth.gif")
    arts: list[Art] = [
        TexturedCircle(75, earth),
        TexturedEllipse(75, 50, earth),
        TexturedPolygon([(0, 0), (100, 100), (0, 100)], earth),
        TexturedRoundedRectangle(earth, 100, 100, 0, 0)
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

# see_geometries()
# see_geometries2()
# see_textures()

# test transformations

def see_transformations():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Rotate, Zoom, Resize, Invert, SetIntroductionIndex, SetIntroductionTime, Transpose
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    arts = [
        earth,
        earth.copy(),
        earth.copy(Rotate(45)),
        earth.copy(Zoom(1/2)),
        earth.copy(Resize((200, 100))),
        earth.copy(Invert()),
        earth.copy(SetIntroductionIndex(7)),
        earth.copy(SetIntroductionTime(300)),
        earth.copy(Transpose())
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_transformations2():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Resize, Flip, Crop, VerticalChop, HorizontalChop, Last, First, ExtractMany, ExtractOne
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    arts = [
        earth,
        earth.copy(Flip(True, False)),
        earth.copy(Crop(50, 50, 100, 100)),
        earth.copy(VerticalChop(50, 100)),
        earth.copy(HorizontalChop(50, 150)),
        earth.copy(Last()),
        earth.copy(First()),
        earth.copy(ExtractMany(8, 15)),
        earth.copy(ExtractOne(17))
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_transformations3():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Resize, Pad, SpeedUp, SlowDown, ResetDuration, ResetDurations, Saturate, Desaturate, ShiftHue
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    earth.load()
    arts = [
        earth,
        earth.copy(Pad((100, 100, 0), 20, 50, 0, 0)),
        earth.copy(SlowDown(2)),
        earth.copy(SpeedUp(2)),
        earth.copy(ResetDurations([10*i for i in range(len(earth.durations))])),
        earth.copy(ResetDuration(250)),
        earth.copy(Saturate(0.7)),
        earth.copy(Desaturate(0.5)),
        earth.copy(ShiftHue(90))
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_transformations4():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Resize, SetAlpha, GrayScale, Gamma, AdjustContrast, AddBrightness, ShiftHue, Darken, Lighten
    from gamarts.mask import GradientCircle
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    arts = [
        earth,
        earth.copy(SetAlpha(100)),
        earth.copy(GrayScale()),
        earth.copy(AdjustContrast(0)),
        earth.copy(Gamma(3)),
        earth.copy(AddBrightness(25)),
        earth.copy(Darken(0.7)),
        earth.copy(ShiftHue(90, GradientCircle(10, 90))),
        earth.copy(Lighten(0.3))
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_transformations5():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Resize, RBGMap, RGBAMap, DrawArc, DrawRectangle, DrawCircle, DrawEllipse, DrawLine, DrawLines
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    arts = [
        earth,
        earth.copy(RBGMap(lambda r,g,b: (r**2, g, b))),
        earth.copy(RGBAMap(lambda r,g,b,a: (r*a, g, b, a))),
        earth.copy(DrawArc((255, 0, 0, 255), (100, 100), 50, 30, 0, 90, 18, 9)),
        earth.copy(DrawRectangle((0, 255, 0, 255), (50, 50, 100, 100), 20)),
        earth.copy(DrawCircle((0, 255, 128, 100), 80, (100, 100), 20)),
        earth.copy(DrawEllipse((0, 255, 128, 100), 80, 50, (100, 100), 20)),
        earth.copy(DrawLine((128, 255, 0, 100), (0, 0), (150, 150), 8)),
        earth.copy(DrawLines((128, 255, 0, 100), [(0, 0), (100, 150), (100, 50), (200, 200)], 8)),
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_transformations6():
    from gamarts import GIFFile
    screen = init()
    screen.fill((255, 255, 255, 255))
    from gamarts.transform import Resize, DrawPolygon, DrawPie, DrawRoundedRectantle
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    arts = [
        earth,
        earth.copy(DrawPolygon((128, 255, 0, 100), [(0, 0), (100, 150), (100, 50), (200, 200)], 8)),
        earth.copy(DrawPie((255, 0, 0, 255), (100, 100), 50, 30, 0, 90, 18, 9)),
        earth.copy(DrawRoundedRectantle((0, 255, 0, 255), (50, 50, 100, 100), 20, 15, thickness=20)),
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_masks1():
    from gamarts import ImageFile
    screen = init()
    from gamarts.transform import ShiftHue, Resize
    from gamarts.mask import Circle, Rectangle, RoundedRectangle, GradientCircle, GradientRectangle, Ellipse, MatrixMask
    import numpy as np
    from ZOCallable.functions import ease_in
    x, y = np.ogrid[:100, :100]
    matrix = (x + y)/200
    lenna = ImageFile("images/Lenna.png", Resize((200, 200)))
    arts = [
        lenna,
        lenna.copy(ShiftHue(90, Circle(70))),
        lenna.copy(ShiftHue(90, Rectangle(0.1, 0.1, 0.5, 0.5))),
        lenna.copy(ShiftHue(90, RoundedRectangle(0.3, 0.3, 0.7, 0.5, 20))),
        lenna.copy(ShiftHue(90, GradientCircle(0.3, 0.8))),
        lenna.copy(ShiftHue(90, GradientRectangle(0.5, 0.7, 0.5, 0.7))),
        lenna.copy(ShiftHue(90, Ellipse(80, 0.3, (0.5, 0.6)))),
        lenna.copy(ShiftHue(90, MatrixMask(matrix))),
        lenna.copy(ShiftHue(90, GradientCircle(0.3, 0.8, ease_in))),
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_masks2():
    from gamarts import ImageFile
    screen = init()
    from gamarts.transform import ShiftHue, Resize
    from gamarts.mask import GradientCircle, Circle, Rectangle, InvertedMask, FromArtAlpha, FromArtColor, FromImageColor, SumOfMasks, ProductOfMasks, AverageOfMasks
    from ZOCallable.functions import ease_in
    lenna = ImageFile("images/Lenna.png", Resize((200, 200)))

    arts = [
        lenna,
        lenna.copy(ShiftHue(90, InvertedMask(Circle(0.6)))),
        lenna.copy(ShiftHue(90, FromArtColor(lenna, lambda r,g,b: (255 + b + g - r)/767))),
        lenna.copy(ShiftHue(90, FromArtAlpha(ImageFile("images/Lenna_alpha.png", Resize((200, 200)))))),
        lenna.copy(ShiftHue(90, FromImageColor("images/Lenna.png", lambda r,g,b: (255 + b + g - r)/767))),
        lenna.copy(ShiftHue(90, SumOfMasks(
            Rectangle(0.1, 0.1, 0.9, 0.9),
            InvertedMask(Rectangle(0.5, 0.5, 0.6, 0.6))
        ))),
        lenna.copy(ShiftHue(90, ProductOfMasks(
           Circle(0.1, (0.2, 0.2)),
           Circle(0.1, (0.5, 0.5)),
           Circle(0.1, (0.8, 0.8)) 
        ))),
        lenna.copy(ShiftHue(90, AverageOfMasks(
            GradientCircle(0.1, 0.4, center=(0.2, 0.2)),
            GradientCircle(0.1, 0.4, center=(0.8, 0.8))
        )))
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

def see_masks3():
    from gamarts import ImageFile
    screen = init()
    from gamarts.transform import ShiftHue, Resize
    from gamarts.mask import BinaryMask, BlitMaskOnMask, TransformedMask, GradientCircle, Circle, DifferenceOfMasks
    lenna = ImageFile("images/Lenna.png", Resize((200, 200)))

    arts = [
        lenna,
        lenna.copy(ShiftHue(90, BinaryMask(GradientCircle(0.2, 0.4), 0.5))),
        lenna.copy(ShiftHue(90, BlitMaskOnMask(GradientCircle(0.1, 0.5), Circle(0.1, (0.7, 0.7)), 0))),
        lenna.copy(ShiftHue(90, TransformedMask(GradientCircle(0.1, 0.5), lambda matrix: matrix**2 + 0.05))),
        lenna.copy(ShiftHue(90, DifferenceOfMasks(
            Circle(0.1),
            Circle(0.5),
        ))),
    ]

    loop(lambda loop_duration: update_and_show(loop_duration, arts, True), screen)

# see_transformations()
# see_transformations2()
# see_transformations3()
# see_transformations4()
# see_transformations5()
# see_transformations6()
# see_masks1()
# see_masks2()
# see_masks3()

def see_reference():
    from gamarts import GIFFile
    screen = init()
    from gamarts.transform import ShiftHue, Resize
    earth = GIFFile("images/wikipedia_earth.gif", Resize((200, 200)))
    ref = earth.reference()
    earth.start()
    ref.start()
    ld_kwargs = {'antialias' : True}
    running = True
    clock = pygame.time.Clock()
    pressed = False
    while running:
        loop_duration = clock.tick(100)
        earth.update(loop_duration)
        ref.update(loop_duration*4/5) # to see the independance between both
        screen.blit(earth.get(**ld_kwargs), (0, 0))
        screen.blit(ref.get(**ld_kwargs), (200, 200))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not pressed:
                earth.transform(ShiftHue(50))
                pressed = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and not pressed:
                ref.transform(ShiftHue(-50))
                pressed = True
            else:
                pressed = False
        pygame.display.flip()
    earth.unload()
    ref.unload()
    pygame.quit()
    
# see_reference()

def test_extractions():
    from gamarts.transform import ExtractTime, ExtractSlice, ExtractWindow
    et = ExtractTime(22)
    es = ExtractSlice(slice(7, 12, 1))
    ew = ExtractWindow(7, 27)
    surfaces = list(range(10))
    intro = 0
    durations = [2]*10
    print(et.apply(surfaces, durations, intro, 0, 0, 0))
    print(es.apply(surfaces, durations, intro, 0, 0, 0))
    print(ew.apply(surfaces, durations, intro, 0, 0, 0))
    intro = 5
    print(et.apply(surfaces, durations, intro, 0, 0, 0))
    print(es.apply(surfaces, durations, intro, 0, 0, 0))
    print(ew.apply(surfaces, durations, intro, 0, 0, 0))


test_extractions()