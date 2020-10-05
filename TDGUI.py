# import pygame
# from pygame.locals import *

# pygame.init()

# white = (255, 255, 255)
# red = (255, 0, 0)
# green = (0, 255, 0)
# blue = (0, 0, 255)
# (width, height) = (300, 200)
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption('Tutorial 1')
# pygame.display.flip()


# RUNNING = True


# while RUNNING:
#     for event in pygame.event.get():
#         print(event)
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             quit()
            
#     screen.fill(white)
#     large_text = pygame.font.Font('freesansbold.ttf',115)

#     pygame.draw.rect(screen, green,(150,450,100,50))
#     pygame.draw.rect(screen, red,(550,450,100,50))


#     pygame.display.update