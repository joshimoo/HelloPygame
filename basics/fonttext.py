import sys
import pygame

from pygame.locals import *

# init pygame
pygame.init()
DISPLAYSURFACE = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('Hello World')

# color constants
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# create text
fontObj = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObj = fontObj.render('Hello World!', True, GREEN, BLUE)
textRectObj = textSurfaceObj.get_rect()
textRectObj.center = (200, 150)

# game loop
while True:

    # process events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # draw
    DISPLAYSURFACE.fill(WHITE)
    DISPLAYSURFACE.blit(textSurfaceObj, textRectObj)
    pygame.display.update()