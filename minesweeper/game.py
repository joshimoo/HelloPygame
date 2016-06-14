import sys
import random
import time
import pygame
import minesweeper.board

from pygame.locals import *


# define constants
FPS = 10

# mouse constants
MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_MIDDLE = 2
MOUSE_BUTTON_RIGHT = 3

# pixel sizes
BASIC_FONT_SIZE = 18
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
CELL_WIDTH = int(WINDOW_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(WINDOW_HEIGHT / CELL_SIZE)
assert WINDOW_WIDTH % CELL_SIZE == 0, 'Window width must be a multiple of cell size.'
assert WINDOW_HEIGHT % CELL_SIZE == 0, 'Window height must be a multiple of cell size.'

# color
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BACKGROUND_COLOR = BLACK

# globals
DISPLAY_SURFACE = None
BASIC_FONT = None
FPS_CLOCK = None

def main():
    global DISPLAY_SURFACE, FPS_CLOCK, BASIC_FONT

    # init pygame
    pygame.init()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Minesweeper')
    FPS_CLOCK = pygame.time.Clock()
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)

    # todo: implement real stateManagment
    # todo: create startGame state, in which user can select board size and game difficulty
    while True:
        runGame()


def makeText(text, color):
    # render(text, antialias, color, background=None) -> Surface)
    textSurface = BASIC_FONT.render(text, True, color)
    textRect = textSurface.get_rect()
    return textSurface, textRect


def drawGameOver():
    textSurface, textRect = makeText('Game Over!!!', RED)
    textRect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    DISPLAY_SURFACE.blit(textSurface, textRect)


def drawGameWon():
    textSurface, textRect = makeText('You Won!!!', GREEN)
    textRect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))
    DISPLAY_SURFACE.blit(textSurface, textRect)


def runGame():
    # mouse handling
    mouseLeftClicked = False
    mouseRightClicked = False
    mouseX = 0
    mouseY = 0

    # board
    board = minesweeper.board.createRandomBoard(WINDOW_WIDTH, WINDOW_HEIGHT)

    # game state
    gameOver = False
    gameWon = False

    # game loop
    while True:

        # process inputs:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_r:
                    return 'reset'  # we return, which will start a new game
            elif event.type == MOUSEBUTTONDOWN:
                # event.button: number value representing the mouse button pressed or released
                # event.pos: X,Y mouse position when the button was pressed or released
                (mouseX, mouseY) = event.pos

                if event.button == MOUSE_BUTTON_LEFT:
                    mouseLeftClicked = True
                elif event.button == MOUSE_BUTTON_RIGHT or event.button == MOUSE_BUTTON_MIDDLE:
                    mouseRightClicked = True

        # update state
        if not gameOver and not gameWon: # game play
            if mouseLeftClicked: # uncover
                # transform screen coords into board coords
                boardX, boardY = screenCordsToBoardCoords(board, mouseX, mouseY)
                result = board.uncover(boardX, boardY)
                if result == 'mine':
                    gameOver = True
                elif result == 'done':
                    gameWon = True
                mouseLeftClicked = False

            if mouseRightClicked: # flag
                # transform screen coords into board coords
                boardX, boardY = screenCordsToBoardCoords(board, mouseX, mouseY)
                board.toggleFlag(boardX, boardY)
                mouseRightClicked = False

        # draw board
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        (boardSurface, boardRect) = board.draw()
        DISPLAY_SURFACE.blit(boardSurface, boardRect)

        # draw game state specifics
        if gameOver:
            # todo: game over do something
            drawGameOver()
        elif gameWon:
            # todo: game won do something
            drawGameWon()
        else:
            # todo: create some nice UI, which displays flag count, solved percentage etc
            pass

        # draw to screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def screenCordsToBoardCoords(board, screenX, screenY):
    # todo: put the board into a specific position and transform and scale accordingly
    # todo: so that it allways fills that specific area, irregardless of cell count
    boardX = int(screenX / board.CELL_WIDTH)
    boardY = int(screenY / board.CELL_HEIGHT)
    return boardX, boardY


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()