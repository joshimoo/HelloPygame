import sys
import pygame

from pygame.locals import *

pygame.init()
DISPLAYSURF = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Hello World!')
while True:  # main game loop

    # process events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # update world state

    # colors
    BLACK = pygame.Color(255, 255, 255)
    RED = pygame.Color('red')
    BLUE = (0, 0, 255)

    # shapes
    # Rect(left, top, width, height) -> Rect
    # Rect((left, top), (width, height)) -> Rect
    c1 = pygame.Rect(10, 20, 200, 300)
    c2 = (10, 20, 200, 300)
    right = c1.right
    # c1 == c2 # --> tuple and Rect object are the same if they have the same values

    # draw updated world
    pygame.display.update()
