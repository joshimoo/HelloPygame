import sys
import random
import pygame
from pygame.locals import *

# define constants
FPS = 30
REVEAL_SPEED = 8

# pixel sizes
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BOX_SIZE = 40
GAP_SIZE = 10

# board size
BOARD_COLS = 10  # COLUMNS
BOARD_ROWS = 7  # ROWS

assert (BOARD_COLS * BOARD_ROWS) % 2 == 0, 'Board needs to have an even number of boxes'
XMARGIN = int((WINDOW_WIDTH - (BOARD_COLS * (BOX_SIZE + GAP_SIZE))) / 2)
YMARGIN = int((WINDOW_HEIGHT - (BOARD_ROWS * (BOX_SIZE + GAP_SIZE))) / 2)

# colors
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BACKGROUND_COLOR = NAVYBLUE
BACKGROUND_LIGHT_COLOR = GRAY
BOX_COLOR = WHITE
HIGHLIGHT_COLOR = BLUE

# shapes
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

# shape colors
ALL_COLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALL_SHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALL_COLORS) * len(ALL_SHAPES) * 2 >= BOARD_COLS * BOARD_ROWS, \
    "Board is too big for the number of shapes/colors defined."


# main function
def main():
    global FPS_CLOCK, DISPLAY_SURFACE

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption('Memory Game')

    # board setup
    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    # mouse
    mouseX = 0
    mouseY = 0

    # selection - stores the (x, y) of the first box clicked
    firstSelection = None

    # inital drawing
    DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
    startGameAnimation(mainBoard)

    # game loop
    while True:
        mouseClicked = False

        # draw
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        drawBoard(mainBoard, revealedBoxes)

        # process input
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouseX, mouseY = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouseX, mouseY = event.pos
                mouseClicked = True

        # update
        boxX, boxY = getBoxAtPixel(mouseX, mouseY)
        if boxX is not None and boxY is not None:
            # the mouse is currently over a box
            if not revealedBoxes[boxY][boxX]:
                drawHighlightBox(boxX, boxY)
            if not revealedBoxes[boxY][boxX] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxX, boxY)])
                revealedBoxes[boxY][boxX] = True
                if firstSelection is None:  # current box was the first selection
                    firstSelection = (boxX, boxY)
                else:  # current box was second box clicked --> evaluate pair
                    firstShape, firstColor = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    secondShape, secondColor = getShapeAndColor(mainBoard, boxX, boxY)
                    if firstShape != secondShape or firstColor != secondColor:  # mismatch
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxX, boxY)])
                        revealedBoxes[firstSelection[1]][firstSelection[0]] = False
                        revealedBoxes[boxY][boxX] = False
                    elif hasWon(revealedBoxes):  # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # show fully unrevealedBoxed for a second
                        # todo: split update and drawing
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # replay the start game animation
                        startGameAnimation(mainBoard)

                    # reset selection
                    firstSelection = None

        # draw screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def generateRevealedBoxesData(isRevealed):
    revealedBoxes = []
    for i in range(BOARD_ROWS):
        revealedBoxes.append([isRevealed] * BOARD_COLS)
    return revealedBoxes


def getRandomizedBoard():
    icons = []
    for color in ALL_COLORS:
        for shape in ALL_SHAPES:
            icons.append((shape, color))

    # randomize order of icon permutation
    random.shuffle(icons)
    requriedUniqueIconCount = int(BOARD_ROWS * BOARD_COLS / 2)
    icons = icons[:requriedUniqueIconCount] * 2  # create two of each
    random.shuffle(icons)

    # create board
    board = []
    for y in range(BOARD_ROWS):
        row = []
        for x in range(BOARD_COLS):
            row.append(icons[0])
            del icons[0]  # remove the icons as we assign them
        board.append(row)
    return board


def splitIntoGroupsOf(groupSize, theList):
    """ splits a list into list of lists,
    where the inner lists have at most
    groupSize number of items.
    """
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxX, boxY):
    """ convert board coordinates into pixel coordinates"""
    left = boxX * (BOX_SIZE + GAP_SIZE) + XMARGIN
    top = boxY * (BOX_SIZE + GAP_SIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    """returns a tuple of board coordinates if x,y matches a box"""
    for boxY in range(BOARD_ROWS):
        for boxX in range(BOARD_COLS):
            left, top = leftTopCoordsOfBox(boxX, boxY)
            boxRect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if boxRect.collidepoint(x, y):  # check whether pixel coordinates are inside box bounds
                return (boxX, boxY)
    return (None, None)  # pixel coordinates don't belong to any box


def drawIcon(shape, color, boxX, boxY):
    """draws the box with the specified board coordinates"""
    quarter = int(BOX_SIZE * 0.25)
    half = int(BOX_SIZE * 0.5)

    # get pixel coordinates from board coordinates
    left, top = leftTopCoordsOfBox(boxX, boxY)

    # draw
    if shape == DONUT:
        pygame.draw.circle(DISPLAY_SURFACE, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAY_SURFACE, BACKGROUND_COLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAY_SURFACE, color, (left + quarter, top + quarter, BOX_SIZE - half, BOX_SIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAY_SURFACE, color, (
            (left + half, top), (left + BOX_SIZE - 1, top + half), (left + half, top + BOX_SIZE - 1),
            (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(DISPLAY_SURFACE, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAY_SURFACE, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAY_SURFACE, color, (left, top + quarter, BOX_SIZE, half))


def getShapeAndColor(board, boxX, boxY):
    """ returns the shape and color for the specified box
    shape is stored in board[boxY][boxX][0]
    color is stored in board[boxY][boxX][1]
    """
    return board[boxY][boxX][0], board[boxY][boxX][1]


def drawBoxCovers(board, boxes, coverage):
    """draws boxes being covered/revealed.
    boxes is a list of two-item lists
    which have the x & y index of the box
    """

    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAY_SURFACE, BACKGROUND_COLOR,(left, top, BOX_SIZE, BOX_SIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])

        # check whether to draw cover
        # todo: this seems wrong
        if coverage > 0:
            pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, coverage, BOX_SIZE))

    # todo: this should not happen inside of this function
    pygame.display.update()
    FPS_CLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    """draws all the boxes in their covered or revealed state"""
    for boxY in range(BOARD_ROWS):
        for boxX in range(BOARD_COLS):
            left, top = leftTopCoordsOfBox(boxX, boxY)

            if not revealed[boxY][boxX]:  # draw covered box
                pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                shape, color = getShapeAndColor(board, boxX, boxY)
                drawIcon(shape, color, boxX, boxY)

def drawHighlightBox(boxX, boxY):
    left, top = leftTopCoordsOfBox(boxX, boxY)
    pygame.draw.rect(DISPLAY_SURFACE, HIGHLIGHT_COLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)

def startGameAnimation(board):
    # randomly reveal the boxes 8 at a time
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for y in range(BOARD_ROWS):
        for x in range(BOARD_COLS):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    # draw the board
    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    colors = [BACKGROUND_COLOR, BACKGROUND_LIGHT_COLOR]
    for i in range(13):
        DISPLAY_SURFACE.fill(colors[i%2])
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:  # is any i false?
            return False
    return True


if __name__ == '__main__':
    # todo: figure out what this does
    main()