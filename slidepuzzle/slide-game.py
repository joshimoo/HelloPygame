import sys
import random
import pygame
from pygame.locals import *

# define constants
FPS = 30
BLANK = None

# pixel sizes
BASIC_FONT_SIZE = 20
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
TILE_SIZE = 80

# board size
BOARD_WIDTH = 4  # COLUMNS
BOARD_HEIGHT = 4  # ROWS
X_MARGIN = int((WINDOW_WIDTH - (TILE_SIZE * BOARD_WIDTH + (BOARD_WIDTH - 1))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (TILE_SIZE * BOARD_HEIGHT + (BOARD_HEIGHT - 1))) / 2)

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 255, 0)

BACKGROUND_COLOR = DARKTURQUOISE
TILE_COLOR = GREEN
TEXT_COLOR = WHITE
BORDER_COLOR = BRIGHTBLUE
BUTTON_COLOR = WHITE
BUTTON_TEXT_COLOR = BLACK
MESSAGE_COLOR = WHITE

# inputs
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, RESET_SURFACE, RESET_RECT, NEW_SURFACE, NEW_RECT, SOLVE_SURFACE, SOLVE_RECT

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)

    # create buttons
    RESET_SURFACE, RESET_RECT = makeText('Reset', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 90)
    NEW_SURFACE, NEW_RECT = makeText('New Game', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60)
    SOLVE_SURFACE, SOLVE_RECT = makeText('Solve', TEXT_COLOR, TILE_COLOR, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 30)

    # create board
    mainBoard, solutionSeq = generateNewPuzzle(80)  # we keep track of the operations that put our board into this state
    SOLVED_BOARD = getStartingBoard()  # a solved board is the same the board in a start state
    allMoves = []  # list of moves made from the solved configuration

    # game loop
    while True:
        msg = ''

        # check whether we have solved the Board
        if mainBoard == SOLVED_BOARD:
            msg = 'Solved!'

        # draw the board
        drawBoard(mainBoard, msg)

        # process input events
        slideTo = None
        checkForQuit()
        for event in pygame.event.get():

            # process mouse events
            if event.type == MOUSEBUTTONUP:
                spotX, spotY = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                # no tiles selected, check whether he hit a button
                if (spotX, spotY) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):  # reset button
                        resetAnimation(mainBoard, allMoves)
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):  # new game button
                        mainBoard, solutionSeq = generateNewPuzzle(80)
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)
                        allMoves = []
                else:
                    # check if the clicked tile was next to the blank spot
                    blankX, blankY = getBlankPosition(mainBoard)
                    if spotX == blankX + 1 and spotY == blankY:
                        slideTo = LEFT
                    elif spotX == blankX - 1 and spotY == blankY:
                        slideTo = RIGHT
                    elif spotX == blankX and spotY == blankY + 1:
                        slideTo = UP
                    elif spotX == blankX and spotY == blankY - 1:
                        slideTo = DOWN

            # process key events
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        # update moves
        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide', 8)
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)  # record the slide

        # draw
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    # get all the quit events
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.type == K_ESCAPE:
            terminate()
        else:  # put the other KEYUP events back in the queue
            pygame.event.post(event)


def getStartingBoard():
    """creates a board data structure with tiles in the solved state
    the board structure is in row major format
    """

    board = []
    for y in range(BOARD_HEIGHT):
        row = []
        for x in range(BOARD_WIDTH):
            row.append(y * BOARD_WIDTH + (x + 1))
        board.append(row)

    # empty last slot
    board[BOARD_HEIGHT - 1][BOARD_WIDTH - 1] = None
    return board


def getBlankPosition(board):
    """returns the board coordinates of the blank space"""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x] is None:
                return (x, y)


def makeMove(board, move):
    """executes a move, does not check if the move is valid"""
    blankX, blankY = getBlankPosition(board)

    # swap the two tiles
    # note: no tmp variable needed, cool python feature :)
    if move == UP:
        board[blankY][blankX], board[blankY + 1][blankX] = \
            board[blankY + 1][blankX], board[blankY][blankX]
    elif move == DOWN:
        board[blankY][blankX], board[blankY - 1][blankX] = \
            board[blankY - 1][blankX], board[blankY][blankX]
    elif move == LEFT:
        board[blankY][blankX], board[blankY][blankX + 1] = \
            board[blankY][blankX + 1], board[blankY][blankX]
    elif move == RIGHT:
        board[blankY][blankX], board[blankY][blankX - 1] = \
            board[blankY][blankX - 1], board[blankY][blankX]


def isValidMove(board, move):
    """verifies that a move is valid"""
    blankX, blankY = getBlankPosition(board)
    return (move == UP and blankY != (len(board) - 1)) or \
           (move == DOWN and blankY != 0) or \
           (move == LEFT and blankX != (len(board[0]) - 1)) or \
           (move == RIGHT and blankX != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the remaining valid moves
    assert len(validMoves) > 0, 'no valid moves, should be impossible'
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = X_MARGIN + (tileX * TILE_SIZE) + (tileX - 1)
    top = Y_MARGIN + (tileY * TILE_SIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    """translate pixel coordinates into board coordinates"""
    for tileY in range(len(board)):
        for tileX in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)

    # not a valid board position
    return (None, None)


def drawTile(tileX, tileY, number, offsetX=0, offsetY=0):
    left, top = getLeftTopOfTile(tileX, tileY)
    pygame.draw.rect(DISPLAY_SURFACE, TILE_COLOR, (left + offsetX, top + offsetY, TILE_SIZE, TILE_SIZE))
    textSurf = BASIC_FONT.render(str(number), True, TEXT_COLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILE_SIZE / 2) + offsetX, top + int(TILE_SIZE / 2) + offsetY
    DISPLAY_SURFACE.blit(textSurf, textRect)


def makeText(text, color, backgroundColor, top, left):
    textSurf = BASIC_FONT.render(text, True, color, backgroundColor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):

    # clear buffer
    DISPLAY_SURFACE.fill(BACKGROUND_COLOR)

    # draw message
    if message:
        textSurf, textRect = makeText(message, MESSAGE_COLOR, BACKGROUND_COLOR, 5, 5)
        DISPLAY_SURFACE.blit(textSurf, textRect)

    # draw tiles
    for tileY in range(len(board)):
        for tileX in range(len(board[0])):
            if board[tileY][tileX]:
                drawTile(tileX, tileY, board[tileY][tileX])

    # draw border
    left, top = getLeftTopOfTile(0, 0)
    width = BOARD_WIDTH * TILE_SIZE
    height = BOARD_HEIGHT * TILE_SIZE
    pygame.draw.rect(DISPLAY_SURFACE, BORDER_COLOR, (left - 5, top - 5, width + 11, height + 11), 4)  # todo: replace magic values

    # draw buttons
    DISPLAY_SURFACE.blit(RESET_SURFACE, RESET_RECT)
    DISPLAY_SURFACE.blit(NEW_SURFACE, NEW_RECT)
    DISPLAY_SURFACE.blit(SOLVE_SURFACE, SOLVE_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    """displays a slow moving tile
    does not check whether the move is valid
    """

    moveX, moveY = None, None
    blankX, blankY = getBlankPosition(board)
    if direction == UP:
        moveX = blankX
        moveY = blankY + 1
    elif direction == DOWN:
        moveX = blankX
        moveY = blankY - 1
    elif direction == LEFT:
        moveX = blankX + 1
        moveY = blankY
    elif direction == RIGHT:
        moveX = blankX - 1
        moveY = blankY
    else:
        assert False, 'invalid move direction'

    # prepare the base surface
    # note: draw order is important
    drawBoard(board, message)
    baseSurf = DISPLAY_SURFACE.copy()

    # draw a blank space over the moving tile on the base Surface
    moveLeft, moveTop = getLeftTopOfTile(moveX, moveY)
    pygame.draw.rect(baseSurf, BACKGROUND_COLOR, (moveLeft, moveTop, TILE_SIZE, TILE_SIZE))

    # animate tile sliding over
    for i in range(0, TILE_SIZE, animationSpeed):
        checkForQuit()  # todo: it sucks having to check here, but loop is blocking
        DISPLAY_SURFACE.blit(baseSurf, (0, 0))  # copy base to display buffer
        if direction == UP:
            drawTile(moveX, moveY, board[moveY][moveX], 0, -i)
        elif direction == DOWN:
            drawTile(moveX, moveY, board[moveY][moveX], 0, i)
        elif direction == LEFT:
            drawTile(moveX, moveY, board[moveY][moveX], -i, 0)
        elif direction == RIGHT:
            drawTile(moveX, moveY, board[moveY][moveX], i, 0)
        else:
            assert False, 'invalid move direction'

    # draw to screen
    pygame.display.update()
    FPS_CLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    """from a starting configuration, make numSlides moves
    also animate these moves
    """
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)
    lastMove = None

    # generate moves
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', int(TILE_SIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move

    # return board and sequences of moves that got us into this configuration
    return (board, sequence)


def resetAnimation(board, allMoves):
    reverseMoves = allMoves[:]  # list copy
    reverseMoves.reverse()  # reverse move list

    for move in reverseMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == LEFT:
            oppositeMove = RIGHT
        elif move == RIGHT:
            oppositeMove = LEFT
        else:
            assert False, 'invalid move direction'

        # execute reverse move
        slideAnimation(board, oppositeMove, '', int(TILE_SIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
        main()