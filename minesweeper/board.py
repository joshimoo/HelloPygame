import random
import pygame

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGRAY = (211, 211, 211)
DARKGRAY = (147, 147, 147)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BACKGROUND_COLOR = BLACK
HIDDEN_COLOR = LIGHTGRAY
VISIBLE_COLOR = DARKGRAY
MINE_COLOR = RED
FLAG_COLOR = BLUE

# map representation
# 0-8 mine count of the neighbourhood
VISIBLE = 16    # visible bit
MINE = 32       # bomb bit
FLAG = 64       # flag bit

# screen position constants
CELL_SIZE = 20

# game constants
MINE_CHANCE = 0.05


def createRandomBoard():
    return createBoard(random.randint(9, 9), random.randint(9, 9), random.randint(5, 15))


def createBoard(width, height, mineCount=None, flagLimit=None):
    board = Board(width, height)

    # make sure that their is enough slots for the requested bombCount
    assert (width * height) >= mineCount, 'not enough space on the board for all these bombs'

    # fill the board
    if mineCount is None:
        mineCount = int((width * height) * MINE_CHANCE)

    if flagLimit is None:  # limit to the amount of nodes :)
        flagLimit = int(width * height) # todo: process flagLimit and mineCount

    # distribute mines randomly
    planted = 0
    while planted < mineCount:
        (x, y) = board.getRandomPosition()
        if board.setMine(x, y):
            planted += 1

    # done return the finished board
    return board


class Board:
    """"this class manages the minesweeper board"""

    def __init__(self, width, height, cellSize=CELL_SIZE):
        """"creates a new board of size width x height"""
        # board params
        self.height = height
        self.width = width
        # self.m = [height][width]
        self.m = [[0 for x in range(0, width)] for y in range(0, height)]
        self.dirty = True

        # create output params
        self.CELL_WIDTH = cellSize
        self.CELL_HEIGHT = cellSize
        self.surface = pygame.Surface((width * self.CELL_WIDTH, height * self.CELL_HEIGHT))
        self.rect = pygame.Rect(0, 0, width * self.CELL_WIDTH, height * self.CELL_HEIGHT)

        # create the text once
        font = pygame.font.Font('freesansbold.ttf', 18)
        self.values = []
        for i in range(0, 10, 1):
            textSurface = font.render('%s' % i, True, BLACK)
            self.values.append(textSurface)

        # accounting
        self.mineCount = 0
        self.flagCount = 0

    def get(self, x, y):
        """returns the node at board position x, y
        if the position is not valid we return False
        since it can be used with Binary Operators
        """
        if not self.validLocation(x, y):
            return False
        return self.m[y][x]

    def _set(self, x, y, bits):
        """or's the passed bits value to the board value at position x, y
        returns False if the position is not valid
        returns True if the operation was successful"""
        if not self.validLocation(x, y):
            return False

        self.dirty = True
        self.m[y][x] |= bits
        return True

    def setMineCount(self, x, y, mineCount):
        return self._set(x, y, mineCount)

    def isVisible(self, x, y):
        return self.get(x, y) & VISIBLE

    def setVisible(self, x, y):
        return self._set(x, y, VISIBLE)

    def hasMine(self, x, y):
        return self.get(x, y) & MINE

    def setMine(self, x, y):
        if not self.hasMine(x, y) and self._set(x, y, MINE):
            self.mineCount += 1
            return True
        return False

    def hasFlag(self, x, y):
        return self.get(x, y) & FLAG

    def setFlag(self, x, y):
        if not self.hasFlag(x, y) and self._set(x, y, FLAG):
            self.flagCount += 1
            return True
        return False

    def removeFlag(self, x, y):
        if not self.hasFlag(x, y):
            return False
        self.m[y][x] &= ~FLAG
        self.dirty = True
        self.flagCount -= 1
        return True

    def getRandomPosition(self):
        return random.randint(0, self.width), random.randint(0, self.height)

    def validLocation(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def uncover(self, x, y):
        if not self.validLocation(x, y):
            return False

        if not self.isVisible(x, y):
            self.dirty = True
            if self.hasMine(x, y):  # we lose
                # todo: update board
                return 'mine'

            # no mines, so flood fill
            self.floodFill(x, y)

        return self.get(x, y)

    def countMines(self, x, y):
        if not self.validLocation(x, y):
            return False

        mineCount = 0
        for yOffset in range(-1, 2, 1):
            for xOffset in range(-1, 2, 1):
                if (x + xOffset == x) and (y + yOffset == y):
                    continue
                if self.hasMine(x + xOffset, y + yOffset):
                    mineCount += 1

        return mineCount

    def floodFill(self, x, y):
        # only process valid locations
        if not self.validLocation(x, y):
            return None

        # we only process nodes that we have not visited before
        # since visible internally checks isValidLocation
        # it could return false, therefore we require
        # an explicit check of isValidLocation at the method entry
        if self.isVisible(x, y):
            return None

        # process cell
        self.setVisible(x, y)
        self.removeFlag(x, y)
        mineCount = self.countMines(x, y)
        if mineCount > 0:  # set count and stop
            self.setMineCount(x, y, mineCount)
            return mineCount

        # flood fill neighbours
        for yOffset in range(-1, 2, 1):
            for xOffset in range(-1, 2, 1):
                if (x + xOffset == x) and (y + yOffset == y):
                    continue
                self.floodFill(x + xOffset, y + yOffset)

    def drawMineCount(self, surface, cellRect, mineCount):
        surface.blit(self.values[mineCount], cellRect)

    def draw(self):
        """"draws the board to a separate surface, only updates the surface, when the board has changed"""
        if not self.dirty:
            return self.surface, self.rect

        # draw board
        for y in range(len(self.m)):
            for x in range(len(self.m[0])):
                leftPos = x * self.CELL_WIDTH
                topPos = y * self.CELL_HEIGHT
                cellRect = pygame.Rect(leftPos, topPos, self.CELL_WIDTH, self.CELL_HEIGHT)

                if not self.isVisible(x, y):
                    pygame.draw.rect(self.surface, HIDDEN_COLOR, cellRect)
                else:
                    pygame.draw.rect(self.surface, VISIBLE_COLOR, cellRect)
                    mineCount = self.m[y][x] & ~(FLAG | MINE | VISIBLE)
                    if mineCount:
                        self.drawMineCount(self.surface, cellRect, mineCount)
                    if self.hasMine(x, y):  # TODO: we uncovered a bomb --> game over
                        pygame.draw.rect(self.surface, MINE_COLOR, cellRect)

                # todo: implement flag handling
                if self.hasFlag(x, y):
                    pygame.draw.rect(self.surface, FLAG_COLOR, cellRect)

        # draw grid lines
        for x in range(0, self.rect.width, self.CELL_WIDTH):  # draw vertical line
            pygame.draw.line(self.surface, BLACK, (x, 0), (x, self.rect.height))
        for y in range(0, self.rect.height, self.CELL_HEIGHT):  # draw horizontal line
            pygame.draw.line(self.surface, BLACK, (0, y), (self.rect.width, y))

        # done return the surface and rect
        return self.surface, self.rect



