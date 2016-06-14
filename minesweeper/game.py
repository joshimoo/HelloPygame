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
BACKGROUND_COLOR = (0, 0, 0)

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

    # mouse handling
    mouseLeftClicked = False
    mouseRightClicked = False
    mouseX = 0
    mouseY = 0

    # board
    board = minesweeper.board.createRandomBoard()

    # game loop
    while True:

        # process inputs:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                # event.button: number value representing the mouse button pressed or released
                # event.pos: X,Y mouse position when the button was pressed or released
                (mouseX, mouseY) = event.pos

                if event.button == MOUSE_BUTTON_LEFT:
                    mouseLeftClicked = True
                elif event.button == MOUSE_BUTTON_RIGHT or event.button == MOUSE_BUTTON_MIDDLE:
                    mouseRightClicked = True

        # update state
        if mouseLeftClicked: # uncover
            # transform screen coords into board coords
            boardX, boardY = screenCordsToBoardCoords(board, mouseX, mouseY)
            board.uncover(boardX, boardY)
            mouseLeftClicked = False

        if mouseRightClicked: # flag
            # transform screen coords into board coords
            boardX, boardY = screenCordsToBoardCoords(board, mouseX, mouseY)
            board.setFlag(boardX, boardY)
            mouseRightClicked = False


        # draw board
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        (boardSurface, boardRect) = board.draw()
        DISPLAY_SURFACE.blit(boardSurface, boardRect)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def screenCordsToBoardCoords(board, screenX, screenY):
    boardX = int(screenX / board.CELL_WIDTH)
    boardY = int(screenY / board.CELL_HEIGHT)
    return boardX, boardY


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()