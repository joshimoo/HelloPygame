import sys
import random
import pygame
from pygame.locals import *

# define constants
FPS = 10
BLANK = None

# pixel sizes
BASIC_FONT_SIZE = 18
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
CELL_WIDTH = int(WINDOW_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(WINDOW_HEIGHT / CELL_SIZE)
assert WINDOW_WIDTH % CELL_SIZE == 0, 'Window width must be a multiple of cell size.'
assert WINDOW_HEIGHT % CELL_SIZE == 0, 'Window height must be a multiple of cell size.'

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)

BACKGROUND_COLOR = BLACK

# inputs
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# snake
HEAD = 0  # index of the worms head

def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)
    pygame.display.set_caption('Good old Snake!')

    # display start screen
    showStartScreen()

    # game loop
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    startX = random.randint(5, CELL_WIDTH - 6)
    startY = random.randint(5, CELL_HEIGHT - 6)
    direction = RIGHT
    snakeCoords = [{'x' : startX,     'y' : startY},
                   {'x' : startX - 1, 'y' : startY},
                   {'x' : startX - 2, 'y' : startY}]

    # create apple
    apple = getRandomLocation()

    # main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and direction != RIGHT:
                    direction = LEFT
                elif event.key in (K_RIGHT, K_d) and direction != LEFT:
                    direction = RIGHT
                elif event.key in (K_UP, K_w) and direction != DOWN:
                    direction = UP
                elif event.key in (K_DOWN, K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # todo: move into separate function
        # check if the snake has hit itself or the edge
        if snakeCoords[HEAD]['x'] == -1 or snakeCoords[HEAD]['x'] == CELL_WIDTH or \
           snakeCoords[HEAD]['y'] == -1 or snakeCoords[HEAD]['y'] == CELL_HEIGHT:
            return  # this will init game over

        for body in snakeCoords[1:]:
            if body['x'] == snakeCoords[HEAD]['x'] and body['y'] == snakeCoords[HEAD]['y']:
                return  # this will init game over

        # check if snake has eaten an apple
        if snakeCoords[HEAD]['x'] == apple['x'] and snakeCoords[HEAD]['y'] == apple['y']:
            # don't remove snakes tail segment
            apple = getRandomLocation()
        else:
            # note: this deletes the tail, it seems pythons indexes are modulos length
            del snakeCoords[-1]

        # create new segment
        if direction == UP:
            newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': snakeCoords[HEAD]['x'] - 1, 'y': snakeCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': snakeCoords[HEAD]['x'] + 1, 'y': snakeCoords[HEAD]['y']}

        # add new segment
        snakeCoords.insert(0, newHead)

        # draw
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        drawGrid()
        drawSnake(snakeCoords)
        drawApple(apple)
        drawScore(len(snakeCoords) - 3)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def drawPressKeyMsg():
    # this call is expensive, better todo this only once
    # and then just blit the Surface & Rect
    pressKeySurf = BASIC_FONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30)
    DISPLAY_SURFACE.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0] == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Snake!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Snake!', True, GREEN)

    degrees1 = 0
    degrees2 = 0

    # start menu loop
    while True:
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)

        # rotate title text
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        DISPLAY_SURFACE.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        DISPLAY_SURFACE.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        # start game on key press
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return

        # update rotation
        degrees1 += 3
        degrees2 += 7

        # draw to screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def showGameOverScreen():
    # create text
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    gameRect = gameSurf.get_rect()
    gameRect.midtop = (WINDOW_WIDTH / 2, 10)

    overSurf = gameOverFont.render('Over', True, WHITE)
    overRect = overSurf.get_rect()
    overRect.midtop = (WINDOW_WIDTH / 2, gameRect.height + 10 + 25)

    # draw text
    DISPLAY_SURFACE.blit(gameSurf, gameRect)
    DISPLAY_SURFACE.blit(overSurf, overRect)
    drawPressKeyMsg()

    # draw to screen
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return  # start new game

def drawScore(score):
    scoreSurf = BASIC_FONT.render('Score: %s' % score, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOW_WIDTH - 120, 10)
    DISPLAY_SURFACE.blit(scoreSurf, scoreRect)


def drawSnake(snakeCoords):
    for coord in snakeCoords:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        segmentRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        innerSegmentRect = pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(DISPLAY_SURFACE, DARKGREEN, segmentRect)
        pygame.draw.rect(DISPLAY_SURFACE, GREEN, innerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELL_SIZE
    y = coord['y'] * CELL_SIZE
    appleRect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(DISPLAY_SURFACE, RED, appleRect)

def drawGrid():
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):  # draw vertical line
        pygame.draw.line(DISPLAY_SURFACE, DARKGRAY, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):  # draw horizontal line
        pygame.draw.line(DISPLAY_SURFACE, DARKGRAY, (0, y), (WINDOW_WIDTH, y))

def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELL_WIDTH - 1), 'y': random.randint(0, CELL_HEIGHT - 1)}


if __name__ == '__main__':
        main()