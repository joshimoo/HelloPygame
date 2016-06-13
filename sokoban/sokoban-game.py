import random
import sys
import copy
import os
import pygame
from pygame.locals import *
from sokoban.asset import *


# constants
FPS = 30

# font sizes
BASIC_FONT_SIZE = 18
BIG_FONT_SIZE = 100

# pixel sizes
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_CENTER = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))

# tile sizes (pixels)
TILE_WIDTH = 50
TILE_HEIGHT = 85
TILE_FLOOR_HEIGHT = 45
TILE_OUTSIDE_DECORATION_PCT = 20  # the percentage of outdoor tiles that have additional decoration (trees, rocks, etc)

# camera controls
CAMERA_DEATH_ZONE = 90  # how far from the center the player can move before moving the camera
CAMERA_MOVE_SPEED = 5  # pixels/per frame

# direction
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHT_BLUE = (0, 170, 255)

# game colors
BACKGROUND_COLOR = BRIGHT_BLUE
TEXT_COLOR = WHITE

# images
ASSET_IMAGE_FILE = 'asset/image/file.png'
ASSET_IMAGE_AVATAR = 'asset/image/squirrel.png'
ASSET_IMAGE_ICON = 'asset/image/gameicon.png'

# fonts
ASSET_FONT_BASIC = 'freesansbold.ttf'

# sound
ASSET_SOUND_FILE = 'asset/sound/file.wav'

# music
ASSET_MUSIC_FILE = 'asset/music/file.mp3'

# level
ASSET_LEVEL_FILE = 'asset/level/201-levels.txt'

# globals
FPS_CLOCK = None
DISPLAY_SURFACE = None
BASIC_FONT = None
IMAGES_DICT = None
TILE_MAPPING = None
OUTSIDE_DECO_MAPPING = None
PLAYER_IMAGES = None
currentImage = None


def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, IMAGES_DICT, TILE_MAPPING, OUTSIDE_DECO_MAPPING, PLAYER_IMAGES, currentImage

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Sokoban: with stars!!!')
    BASIC_FONT = pygame.font.Font(ASSET_FONT_BASIC, BASIC_FONT_SIZE)

    # A global dict value that will contain all the Pygame
    # Surface objects returned by pygame.image.load().
    IMAGES_DICT = {'uncovered goal': pygame.image.load('asset/image/RedSelector.png'),
                  'covered goal': pygame.image.load('asset/image/Selector.png'),
                  'star': pygame.image.load('asset/image/Star.png'),
                  'corner': pygame.image.load('asset/image/Wall_Block_Tall.png'),
                  'wall': pygame.image.load('asset/image/Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('asset/image/Plain_Block.png'),
                  'outside floor': pygame.image.load('asset/image/Grass_Block.png'),
                  'title': pygame.image.load('asset/image/star_title.png'),
                  'solved': pygame.image.load('asset/image/star_solved.png'),
                  'princess': pygame.image.load('asset/image/princess.png'),
                  'boy': pygame.image.load('asset/image/boy.png'),
                  'catgirl': pygame.image.load('asset/image/catgirl.png'),
                  'horngirl': pygame.image.load('asset/image/horngirl.png'),
                  'pinkgirl': pygame.image.load('asset/image/pinkgirl.png'),
                  'rock': pygame.image.load('asset/image/Rock.png'),
                  'short tree': pygame.image.load('asset/image/Tree_Short.png'),
                  'tall tree': pygame.image.load('asset/image/Tree_Tall.png'),
                  'ugly tree': pygame.image.load('asset/image/Tree_Ugly.png')}

    # These dict values are global, and map the character that appears
    # in the level file to the Surface object it represents.
    TILE_MAPPING = {'x': IMAGES_DICT['corner'],
                    '#': IMAGES_DICT['wall'],
                    'o': IMAGES_DICT['inside floor'],
                    ' ': IMAGES_DICT['outside floor']}
    OUTSIDE_DECO_MAPPING = {'1': IMAGES_DICT['rock'],
                            '2': IMAGES_DICT['short tree'],
                            '3': IMAGES_DICT['tall tree'],
                            '4': IMAGES_DICT['ugly tree']}

    # PLAYER_IMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    PLAYER_IMAGES = [IMAGES_DICT['princess'],
                    IMAGES_DICT['boy'],
                    IMAGES_DICT['catgirl'],
                    IMAGES_DICT['horngirl'],
                    IMAGES_DICT['pinkgirl']]

    # show the start screen
    startScreen()

    # read in the levels from the text file. See the readLevelFile() for
    # details on the format of this file and how to make your own levels.
    levels = readLevelFile(ASSET_LEVEL_FILE)
    currentLevelIndex = 0

    # the main game loop, this loop runs a single level, when the user
    # finishes that level, the next/previous level is loaded
    while True:
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):  # next level
            # no more levels restart from the beginning
            currentLevelIndex = int((currentLevelIndex + 1) % len(levels))
        elif result == 'back':  # prev level
            # no more levels start with the last
            currentLevelIndex = int((currentLevelIndex - 1) % len(levels))
        elif result == 'reset':  # reset level
            pass  # do nothing loop re-calls runLevel() to reset the level


def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True  # set to true, to call draw map
    levelSurf = BASIC_FONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXT_COLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINDOW_HEIGHT - 35)
    mapWidth = len(mapObj) * TILE_WIDTH
    mapHeight = (len(mapObj[0]) - 1) * (TILE_HEIGHT - TILE_FLOOR_HEIGHT) + TILE_HEIGHT
    # todo: i think height and width is mixed
    CAMERA_MAX_X_PAN = abs(WINDOW_CENTER[1] - int(mapHeight / 2)) + TILE_WIDTH
    CAMERA_MAX_Y_PAN = abs(WINDOW_CENTER[0] - int(mapWidth / 2)) + TILE_HEIGHT
    levelIsComplete = False

    # track camera
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    # game loop
    while True:
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                keyPressed = True

                # move player
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                # move camera
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                # switch level
                elif event.key == K_n:  # next level
                    return 'next'
                elif event.key == K_b:  # prev level
                    return 'back'
                elif event.key == K_BACKSPACE:  # reset level
                    return 'reset'

                # switch player image
                elif event.key == K_p:
                    currentImage = int((currentImage + 1) % len(PLAYER_IMAGES))
                    mapNeedsRedraw = True

                # quit
                elif event.key == K_ESCAPE:
                    terminate()

            elif event.type == KEYUP:
                # unset camera move mode
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo is not None and not levelIsComplete:
            # if the player pushed a key to move, make the move
            # (if possible) and push any stars/boxes that are pushable
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved: # increment step counter
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj): # level is solved
                levelIsComplete = True
                keyPressed = False

        # draw background
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)

        # update map
        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        # update camera
        if cameraUp and cameraOffsetY < CAMERA_MAX_X_PAN:
            cameraOffsetY += CAMERA_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -CAMERA_MAX_X_PAN:
            cameraOffsetY -= CAMERA_MOVE_SPEED
        if cameraLeft and cameraOffsetX < CAMERA_MAX_Y_PAN:
            cameraOffsetX += CAMERA_MOVE_SPEED
        elif cameraRight and cameraOffsetY > -CAMERA_MAX_Y_PAN:
            cameraOffsetX -= CAMERA_MOVE_SPEED

        # adjust map rect based on camera
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (WINDOW_CENTER[0] + cameraOffsetX, WINDOW_CENTER[1] + cameraOffsetY)

        # draw()
        DISPLAY_SURFACE.blit(mapSurf, mapSurfRect)
        DISPLAY_SURFACE.blit(levelSurf, levelRect)
        stepSurf = BASIC_FONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXT_COLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINDOW_HEIGHT - 10)
        DISPLAY_SURFACE.blit(stepSurf, stepRect)

        if levelIsComplete:
            # show the "Solved!" image until the player has pressed a key
            solvedRect = IMAGES_DICT['solved'].get_rect()
            solvedRect.center = (WINDOW_CENTER[0], WINDOW_CENTER[1])
            DISPLAY_SURFACE.blit(IMAGES_DICT['solved'], solvedRect)

            # start next level
            if keyPressed:
                return 'solved'

        # draw to screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def isWall(mapObj, x, y):
    """Returns True if the (x, y) position on
    the map is a wall, otherwise return False."""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # x and y aren't actually on the map.
    elif mapObj[x][y] in ('#', 'x'):
        return True # wall is blocking
    return False

def decorateMap(mapObj, startPostion):
    """makes a copy of the given mapObj and modifies it
    here is what is done to it:
        * walls that are corders are turned into corner pieces
        * the outside/floor tile distinction is made
        * tree/rock decorations are randomly added to the outside tiles
    returns the decoration mapObj
    """
    startX, startY = startPostion

    # copy the mapObj so we don't modify the original
    mapObjCopy = copy.deepcopy(mapObj)

    # remove the non-wall characters from the map data
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    # flood fill to determine inside/outside floor tiles
    floodFill(mapObjCopy, startX, startY, ' ', 'o')

    # convert the adjoined walls into corner tiles
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            # is wall
            if mapObjCopy[x][y] == '#':
                # check neighbours
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x + 1, y)) or \
                    (isWall(mapObjCopy, x, y + 1) and isWall(mapObjCopy, x - 1, y)) or \
                    (isWall(mapObjCopy, x + 1, y) and isWall(mapObjCopy, x, y + 1)) or \
                    (isWall(mapObjCopy, x - 1, y) and isWall(mapObjCopy, x, y - 1)):

                    # two adjacent tiles are walls, so we can make a corner
                    mapObjCopy[x][y] = 'x'

            # check whether to place decoration
            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < TILE_OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDE_DECO_MAPPING.keys()))

    # return the modified map
    return mapObjCopy

def isBlocked(mapObj, gameStateObj, x, y):
    """"returns true if the (x,y) position on the map is
    blocked by a wall or star, otherwise return False
    """

    if isWall(mapObj, x, y):
        return True  # wall is blocking

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True  # x or y are not actually on the map

    elif (x, y) in gameStateObj['stars']:
        return True  # star is blocking

    # target position is free
    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    """"given a map and game state object, see if it is possible for the
    player to make the given move. if it is, then change the player's position
    and the position of any pushed stars. if not do nothing

    returns True if the player moved, otherwise False
    """

    playerX, playerY = gameStateObj['player']
    stars = gameStateObj['stars']

    # the code for handling each of the directions is so similiar
    # aside from adding or subtracting 1 to the x/y coords, we can
    # simplify it by using the xOffset and yOffset variables
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    # check if a wall blocks us
    if isWall(mapObj, playerX + xOffset, playerY + yOffset):
        return False

    # check if a star blocks us
    if (playerX + xOffset, playerY + yOffset) in stars:

        # check if the spot behind the star is free (considers the movement direction)
        if not isBlocked(mapObj, gameStateObj, (playerX + xOffset * 2), (playerY + yOffset * 2)):
            # move the star
            index = stars.index((playerX + xOffset, playerY + yOffset))
            stars[index] = (stars[index][0] + xOffset, stars[index][1] + yOffset)
        else:  # cannot move star
            return False

    # move player
    gameStateObj['player'] = (playerX + xOffset, playerY + yOffset)
    return True


def startScreen():
    """"display the start screen with title and instructions
    until the player presses a key -> returns None
    """
    titleRect = IMAGES_DICT['title'].get_rect()
    top = 50 # where to position the top of the text
    titleRect.top = top
    titleRect.centerx = WINDOW_CENTER[0]
    top += titleRect.height

    # unfortunatly pygames font & text system only shows one line at
    # a time, so we can't use strings with newline characters (\n) in them
    # so instead we will use a list with each line in it
    instructionText = ['Push the stars over the marks',
                       'Arrow keys to move, WASD for camera control, P to change character',
                       'Backspace to reset level, ESC to quit',
                       'N for next level, B to go back a level']

    # clear window
    DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
    DISPLAY_SURFACE.blit(IMAGES_DICT['title'], titleRect)

    # position and draw the text
    for i in range(len(instructionText)):
        instSurf = BASIC_FONT.render(instructionText[i], 1, TEXT_COLOR)
        instRect = instSurf.get_rect()
        top += 10  # leave 10 pixels between each line
        instRect.top = top
        instRect.centerx = WINDOW_CENTER[0]
        top += instRect.height # adjust for the height of the line
        DISPLAY_SURFACE.blit(instSurf, instRect)

    # main loop for the start screen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

                # user pressed a key so return
                return

        # draw to the screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def readLevelFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file %s' % filename

    # each level must end with a blank line
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    # content into levels
    levels = []         # will contain a list of level objects
    levelNum = 0
    mapTextLines = []   # contains the lines for a single level's map
    mapObj = []         # the map object made from the data in mapTextLines
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')

        # check for comments in the line
        if ';' in line:
            line = line[:line.find(';')]

        # process line
        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # a blank line indicates the end of a level's map in the file
            # convert the text in mapTextLine into a level object.

            # find the longest row in the map
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])

            # add spaces to the ends of the shorter rows
            # this ensures the map will be rectangular
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # convert text to a mapObj
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # loop through the spaces in the map and find the
            # @, ., and $ characters for the starting game state
            startX = None
            startY = None
            goals = []      # list of (x,y) tuples for each goal
            stars = []      # list of (x,y) tuples for each star

            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' is a player
                        # '+' is a player and goal
                        startX = x
                        startY = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' is a goal
                        # '+' is a player and goal
                        # '*' is a star and goal
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' is a star
                        # '*' is a star and goal
                        stars.append((x, y))

            # level design sanity checks:
            assert startX != None and startY != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))
            # todo: should't len(stars) == len(goals) be valid?

            # create level object and starting game state object
            gameStateObj = {'player': (startX, startY),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}
            levels.append(levelObj)

            # reset the variables for reading the next map
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1

    # done return all levels
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    """"changes any values matching oldCharacter on the map object to
    newCharacter at the (x,y) position, and does the same for the
    positions to the left, right, down and up of (x,y) recursively
    """

    # change current node
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    # check neighbours
    if (x < len(mapObj) - 1) and mapObj[x + 1][y] == oldCharacter:  # right
        floodFill(mapObj, x + 1, y, oldCharacter, newCharacter)
    if (x > 0) and mapObj[x - 1][y] == oldCharacter:  # left
        floodFill(mapObj, x - 1, y, oldCharacter, newCharacter)
    if (y < len(mapObj[x]) - 1) and mapObj[x][y + 1] == oldCharacter:  # down
        floodFill(mapObj, x, y + 1, oldCharacter, newCharacter)
    if (y > 0) and mapObj[x][y - 1] == oldCharacter:  # up
        floodFill(mapObj, x, y - 1, oldCharacter, newCharacter)

def drawMap(mapObj, gameStateObj, goals):
    """draws the map to a surface object, including the player and stars
    this function does not call pygame.display.update() nor does
    it draw the "Level"  and "Steps" text in the corner
    """

    # mapSurf will be the single Surface object that the tiles are drawn on
    # so that it is easy to position the entire map on the DISPLAY_SURFACE object
    # first the width and height must be calculate
    mapSurfWidth = len(mapObj) * TILE_WIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * (TILE_HEIGHT - TILE_FLOOR_HEIGHT) + TILE_HEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BACKGROUND_COLOR)

    # draw tile sprites
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILE_WIDTH, y * (TILE_HEIGHT - TILE_FLOOR_HEIGHT), TILE_WIDTH, TILE_HEIGHT))
            if mapObj[x][y] in TILE_MAPPING:
                baseTile = TILE_MAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDE_DECO_MAPPING:
                baseTile = TILE_MAPPING[' ']

            # first draw the base ground/wall tile
            mapSurf.blit(baseTile, spaceRect)

            # draw any tree/rock decorations are on this tile
            if mapObj[x][y] in OUTSIDE_DECO_MAPPING:
                mapSurf.blit(OUTSIDE_DECO_MAPPING[mapObj[x][y]], spaceRect)

            elif (x, y) in gameStateObj['stars']:
                if (x,y) in goals:
                    # goal & star on this space, draw goal first
                    mapSurf.blit(IMAGES_DICT['covered goal'], spaceRect)

                # then draw the star
                mapSurf.blit(IMAGES_DICT['star'], spaceRect)

            elif (x, y) in goals:
                # draw a goal withhout a star on it
                mapSurf.blit(IMAGES_DICT['uncovered goal'], spaceRect)

            # last draw the player on the field
            if (x, y) == gameStateObj['player']:
                # note: the value ""currentImage" refers to a key in
                # "PLAYER_IMAGES" which has the specific image
                mapSurf.blit(PLAYER_IMAGES[currentImage], spaceRect)

    # done return the map surface
    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    """"returns true if all the goals have stars in them"""
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            # found a space with a goal but no star on it
            return False

    # all goals are covered
    return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()




















