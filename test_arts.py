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
        func(loop_duration, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()

ld_kwargs = {
    'antialias' : True,
    # So far, it is the only one that is needed.
}

def update_and_show(loop_duration, screen, art):
    art.update(loop_duration)
    screen.blit(art.get(**ld_kwargs), (0, 0))

# Test arts from files

def see_image_no_alpha():
    from gamarts.art import ImageFile
    lenna = ImageFile("images/Lenna.png")
    screen = init()
    
    loop(lambda loop_duration, screen: update_and_show(loop_duration, screen, lenna), screen)

def see_image_alpha():
    from gamarts.art import ImageFile
    lenna = ImageFile("images/Lenna_alpha.png")
    screen = init()
    
    loop(lambda loop_duration, screen: update_and_show(loop_duration, screen, lenna), screen)

def see_gif():
    from gamarts.art import GIFFile
    earth = GIFFile("images/wikipedia_earth.gif")
    screen = init()
    loop(lambda loop_duration, screen: update_and_show(loop_duration, screen, earth), screen)
    
def see_folder():
    from gamarts.art import ImageFolder
    squares = ImageFolder("images/squares", 700)
    screen = init()
    loop(lambda loop_duration, screen: update_and_show(loop_duration, screen, squares), screen)
    

# see_image_no_alpha()
# see_image_alpha()
# see_gif()
see_folder()