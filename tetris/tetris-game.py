import sys
import random
import time
import pygame
from pygame.locals import *

# define constants
FPS = 25

# movement
MOVE_SIDEWAYS_FREQ = 0.15
MOVE_DOWN_FREQ = 0.1

# pixel sizes
BASIC_FONT_SIZE = 18
BIG_FONT_SIZE = 100
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# board sizes
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOX_SIZE = 20
BLANK = '.'

# margin sizes
X_MARGIN = int((WINDOW_WIDTH - BOARD_WIDTH * BOX_SIZE) / 2)
TOP_MARGIN = WINDOW_HEIGHT - (BOARD_HEIGHT * BOX_SIZE) - 5

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
RED = (255, 0, 0)
LIGHTRED = (175, 20, 20)
GREEN = (0, 255, 0)
LIGHTGREEN = (20, 175, 20)
BLUE = (0, 0, 255)
LIGHTBLUE = (20, 20, 175)
YELLOW = (155, 155, 0)
LIGHTYELLOW = (175, 175, 20)

# game colors
BACKGROUND_COLOR = BLACK
BORDER_COLOR = BLUE
TEXT_COLOR = WHITE
TEXT_SHADOW_COLOR = GRAY

# block colors
COLORS = (BLUE, GREEN, RED, YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS), 'each color must have a light color equivalent'

# piece sizes
TEMPLATE_WIDTH = 5
TEMPLATE_HEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

# inputs
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, BIG_FONT

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', BASIC_FONT_SIZE)
    BIG_FONT = pygame.font.Font('freesansbold.ttf', BIG_FONT_SIZE)
    pygame.display.set_caption('Good old Tetris!')

    # show text screen
    showTextScreen('Tetris')
    while True:
        # load random music
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('assets/tetrisb.mid')
        else:
            pygame.mixer.music.load('assets/tetrisc.mid')

        # play music
        pygame.mixer.music.play(-1, 0.0)
        runGame()
        pygame.mixer.stop()
        showTextScreen('Game Over')


def runGame():
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSideWaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    while True:

        # no falling piece in play, create a new one at the top
        if fallingPiece == None:
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time()

            if not isValidPosition(board, fallingPiece):
                return  # game over

        # process-input()
        # process events
        checkForQuit()
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_p:  # pause game
                    DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused') # pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSideWaysTime = time.time()
                elif event.key == K_LEFT or event.key == K_a:
                    movingLeft = False
                elif event.key == K_RIGHT or event.key == K_d:
                    movingRight = False
                elif event.key == K_DOWN or event.key == K_s:
                    movingDown = False

            elif event.type == KEYDOWN:
                # moving sideways
                if (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSideWaysTime = time.time()
                elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSideWaysTime = time.time()

                # rotate shape if there is space
                elif event.key == K_UP or event.key == K_w: # clockwise
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece): # undo rotation
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])

                elif event.key == K_q: # counter clockwise
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece): # undo rotation
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])

                # make block fall faster
                elif event.key == K_DOWN or event.key == K_s:
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()

                # move the current block all the way down
                elif event.key == K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARD_HEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):  # lower as far as possible
                            break
                    fallingPiece['y'] += i - 1

        # update()
        # handle moving the block because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSideWaysTime > MOVE_SIDEWAYS_FREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSideWaysTime = time.time()

        if movingDown and time.time() - lastMoveDownTime > MOVE_DOWN_FREQ and isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            if not isValidPosition(board, fallingPiece, adjY=1): # landed
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
            else: # not landed move the block
                fallingPiece['y'] += 1
                lastFallTime = time.time()


        # draw()
        # draw everything to the screen
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    # so that we don't potentially lose events
    checkForQuit()
    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYUP:
            return event.key

    # no key up
    return None


def showTextScreen(text):
    """this function displays large text in the center
    of the screen until a key is pressed
    """
    # draw the shadow
    titleSurf, titleRect = makeTextObjs(text, BIG_FONT, TEXT_SHADOW_COLOR)
    titleRect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))
    DISPLAY_SURFACE.blit(titleSurf, titleRect)

    # draw the text
    titleSurf, titleRect = makeTextObjs(text, BIG_FONT, TEXT_COLOR)
    titleRect.center = (int(WINDOW_WIDTH / 2) - 3, int(WINDOW_HEIGHT / 2) - 3)
    DISPLAY_SURFACE.blit(titleSurf, titleRect)

    # press a key text
    titleSurf, titleRect = makeTextObjs('Press a key to play.', BASIC_FONT, TEXT_COLOR)
    titleRect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2) + 100)
    DISPLAY_SURFACE.blit(titleSurf, titleRect)

    # evaluate keypress
    while checkForKeyPress() == None:
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def checkForQuit():
    # get all the quit events
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.type == K_ESCAPE:
            terminate()
        else:  # put the other KEYUP events back in the queue
            pygame.event.post(event)


def calculateLevelAndFallFreq(score):
    """based on the score, return the level the player is on
    and how many seconds pass until a falling piece falls one step
    """
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq


def getNewPiece():
    """return a random new piece in a random rotation and color"""
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARD_WIDTH / 2) - int(TEMPLATE_WIDTH / 2),
                'y': -2, # start it above the board
                'color': random.randint(0, len(COLORS) - 1)}
    return newPiece


def addToBoard(board, piece):
    for y in range(TEMPLATE_HEIGHT):
        for x in range(TEMPLATE_WIDTH):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[y + piece['y']][x + piece['x']] = piece['color']


def getBlankBoard():
    """creates an empty board"""
    board = []
    for i in range(BOARD_HEIGHT):
        board.append([BLANK] * BOARD_WIDTH)
    return board


def isOnBoard(x, y):
    # note: cool python syntax for comparison with constants
    return 0 <= x < BOARD_WIDTH and y < BOARD_HEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    """returns true, if the piece is withing the board and not colliding"""
    for y in range(TEMPLATE_HEIGHT):
        for x in range(TEMPLATE_WIDTH):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:  # just started
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):  # out of bounds
                return False
            if board[y + piece['y'] + adjY][x + piece['x'] + adjX] != BLANK:  # collision
                return

    # valid position
    return True


def isCompleteLine(board, y):
    """returns true if the line does not contain any free spots"""
    for x in range(BOARD_WIDTH):
        if board[y][x] == BLANK:
            return False
    return True


def removeCompleteLines(board):
    """remove any completed lines on the board,
    move everything above them down,
    and return the number of completed lines
    """
    numLinesRemoved = 0
    y = BOARD_HEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # remove the line and pull boxes down by one line
            for pullDownY in range(y, 0, -1):
                for x in range(BOARD_WIDTH):
                    board[pullDownY][x] = board[pullDownY - 1][x]

            # set very top line to blank
            for x in range(BOARD_WIDTH):
                board[0][x] = BLANK
            numLinesRemoved += 1

        # only increment y, when we did not remove a line
        # otherwise we skip checking whether the pulled down boxes
        # form a complete line
        else:
            y -= 1

    # return the amount of removed lines
    return numLinesRemoved


def convertToPixelCoords(boxX, boxY):
    """convert the given xy board coordinates to screen coordinates"""
    return (X_MARGIN + (boxX * BOX_SIZE)), (TOP_MARGIN + (boxY * BOX_SIZE))


def drawBox(boxX, boxY, color, pixelX=None, pixelY=None):
    """draw a single box (each piece has four boxes)
    at xy coordinates on the board. Or, if pixelX & pixelY
    are specified, draw to the pixel coordinates stored in
    pixelX & pixelY (this is used for nextPiece
    """

    if color == BLANK:
        return
    if pixelX is None and pixelY is None:
        pixelX, pixelY = convertToPixelCoords(boxX, boxY)

    # draw to pixel coordinates
    pygame.draw.rect(DISPLAY_SURFACE, COLORS[color], (pixelX + 1, pixelY + 1, BOX_SIZE - 1, BOX_SIZE - 1))
    pygame.draw.rect(DISPLAY_SURFACE, LIGHTCOLORS[color], (pixelX + 1, pixelY + 1, BOX_SIZE - 4, BOX_SIZE - 4))


def drawBoard(board):
    # draw border
    pygame.draw.rect(DISPLAY_SURFACE, BORDER_COLOR, (X_MARGIN - 3, TOP_MARGIN - 7, (BOARD_WIDTH * BOX_SIZE) + 8, (BOARD_HEIGHT * BOX_SIZE) + 8), 5)

    # draw background of the board
    pygame.draw.rect(DISPLAY_SURFACE, BACKGROUND_COLOR, (X_MARGIN, TOP_MARGIN, BOX_SIZE * BOARD_WIDTH, BOX_SIZE * BOARD_HEIGHT))

    # draw boxes
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            drawBox(x, y, board[y][x])


def drawStatus(score, level):
    """draws score & level text"""
    scoreSurf = BASIC_FONT.render('Score: %s' % score, True, TEXT_COLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOW_WIDTH - 150, 20)
    DISPLAY_SURFACE.blit(scoreSurf, scoreRect)

    levelSurf = BASIC_FONT.render('Level: %s' % level, True, TEXT_COLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOW_WIDTH - 150, 50)
    DISPLAY_SURFACE.blit(levelSurf, levelRect)


def drawPiece(piece, pixelX=None, pixelY=None):
    """draws a piece either on the passed pixel coords
    or uses the pieces board position
    to calculate the screen position
    """
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelX is None and pixelY is None:
        # if no pixel position specified, use location data from the piece
        pixelX, pixelY = convertToPixelCoords(piece['x'], piece['y'])

    # draw each block from the shape
    for y in range(TEMPLATE_HEIGHT):
        for x in range(TEMPLATE_WIDTH):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelX + (x * BOX_SIZE), pixelY + (y * BOX_SIZE))


def drawNextPiece(piece):
    # draw next text
    nextSurf = BASIC_FONT.render('Next:', True, TEXT_COLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOW_WIDTH - 120, 80)
    DISPLAY_SURFACE.blit(nextSurf, nextRect)

    #draw the next piece (outside playing field)
    drawPiece(piece, pixelX=WINDOW_WIDTH-120, pixelY=100)


if __name__ == '__main__':
    main()
