import sys
import pygame

from pygame.locals import *


# init pygame
pygame.init()

FPS = 30
fpsClock = pygame.time.Clock()

# setup window
DISPLAYSURFACE = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption("Animation")

WHITE = (255, 255, 255)
catImg = pygame.image.load('cat.png')
catX = 10
catY = 10
catDir = 'right'

# game loop
while True:

    # process events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # move cat
    if catDir == 'right':
        catX += 5
        if catX == 280:
            catDir = 'down'
    elif catDir == 'down':
        catY += 5
        if catY == 220:
            catDir = 'left'
    elif catDir == 'left':
        catX -= 5
        if catX == 10:
            catDir = 'up'
    elif catDir == 'up':
        catY -= 5
        if catY == 10:
            catDir = 'right'

    # draw cat
    DISPLAYSURFACE.fill(WHITE)  # clear buffer
    DISPLAYSURFACE.blit(catImg, (catX, catY))

    # draw buffer to screen
    pygame.display.update()
    fpsClock.tick(FPS)  # delay so that we have 30 frames per second





