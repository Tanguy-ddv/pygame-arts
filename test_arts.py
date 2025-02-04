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

    arts[0].save("circle.png", 1)


# see_geometries()
# see_geometries2()
see_textures()
