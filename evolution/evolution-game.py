import sys
import random
import time
import math
import pygame
from pygame.locals import *

# define constants
FPS = 30

# pixel sizes
BASIC_FONT_SIZE = 32
BIG_FONT_SIZE = 100
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_CENTER = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))

# camera controls
CAMERA_DEATH_ZONE = 90  # how far from the center the player can move before moving the camera

# player controls
MAX_HEALTH = 3
MOVE_RATE = 9
BOUNCE_RATE = 6  # larger is slower
BOUNCE_HEIGHT = 30
START_SIZE = 25
WIN_SIZE = 300
INVULNERABILITY_TIME = 2
GAME_OVER_TIME = 4

# world params
NUM_GRASS = 80  # number of grass objects in the active area
NUM_ENEMIES = 30
ENEMY_MIN_SPEED = 3
ENEMY_MAX_SPEED = 7
ENEMY_DIR_CHANGE_FREQ = 2  # 2% chance of direction change per frame

# direction
LEFT = 'left'
RIGHT = 'right'

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
GRASS_COLOR = (24, 255, 0)

# globals
FPS_CLOCK = None
DISPLAY_SURFACE = None
BASIC_FONT = None
AVATAR_L_IMG = None
AVATAR_R_IMG = None
GRASS_IMAGES = []

# assets
ASSET_IMG_GRASS_TEMPLATE = 'assets/grass%s.png'
ASSET_IMG_AVATAR = 'assets/squirrel.png'
ASSET_IMG_ICON = 'assets/gameicon.png'
ASSET_FONT_BASIC = 'freesansbold.ttf'


def main():
    global FPS_CLOCK, DISPLAY_SURFACE, BASIC_FONT, AVATAR_L_IMG, AVATAR_R_IMG, GRASS_IMAGES

    # init pygame
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_icon(pygame.image.load(ASSET_IMG_ICON))
    pygame.display.set_caption('Evolution - grow or die!')
    BASIC_FONT = pygame.font.Font(ASSET_FONT_BASIC, BASIC_FONT_SIZE)

    # load the image files
    AVATAR_L_IMG = pygame.image.load(ASSET_IMG_AVATAR)
    AVATAR_R_IMG = pygame.transform.flip(AVATAR_L_IMG, True, False)
    GRASS_IMAGES = []
    for i in range(1, 5):
        GRASS_IMAGES.append(pygame.image.load(ASSET_IMG_GRASS_TEMPLATE % i))

    while True:
        runGame()


def createText(text, center_pos, color=WHITE):
    surf = BASIC_FONT.render(text, True, color)
    rect = surf.get_rect()
    rect.center = center_pos
    return surf, rect


def runGame():
    """ init variables for the start of a new game """
    invulnerableMode = False
    invulnerableStartTime = 0
    gameOverMode = False
    gameOverStartTime = 0
    winMode = False

    # create surface to hold game
    gameOverSurf, gameOverRect = createText('Game Over', WINDOW_CENTER)
    winSurf, winRect = createText('You have climbed to the top of the food chain', WINDOW_CENTER)
    win2Surf,win2Rect = createText('Press "r" to restart', (WINDOW_CENTER[0], WINDOW_CENTER[1] + 30))

    # setup camera
    cameraX = 0
    cameraY = 0

    # entities
    grassObjs = []
    enemyObjs = []
    playerObj = {
        'surface': pygame.transform.scale(AVATAR_L_IMG, (START_SIZE, START_SIZE)),
        'facing': LEFT,
        'size': START_SIZE,
        'x': WINDOW_CENTER[0],
        'y': WINDOW_CENTER[1],
        'bounce': 0,
        'health': MAX_HEALTH
    }

    # input
    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False

    # create starting grass
    for i in range(10):
        grassObjs.append(makeGrass(cameraX, cameraY))
        grassObjs[i]['x'] = random.randint(0, WINDOW_WIDTH)
        grassObjs[i]['y'] = random.randint(0, WINDOW_HEIGHT)

    # game loop
    while True:
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNERABILITY_TIME:
            invulnerableMode = False

        # update all the enemies
        for enemy in enemyObjs:
            enemy['x'] += enemy['moveX']
            enemy['y'] += enemy['moveY']

            # update bounce
            enemy['bounce'] += 1
            if enemy['bounce'] > enemy['bounceRate']:
                enemy['bounce'] = 0  # reset bounce amount

            # random chance that they change direction
            if random.randint(0, 99) < ENEMY_DIR_CHANGE_FREQ:
                enemy['moveX'] = getRandomVelocity()
                enemy['moveY'] = getRandomVelocity()
                if enemy['moveX'] > 0: # faces right
                    enemy['surface'] = pygame.transform.scale(AVATAR_R_IMG, (enemy['width'], enemy['height']))
                else: # face left
                    enemy['surface'] = pygame.transform.scale(AVATAR_L_IMG, (enemy['width'], enemy['height']))


        # delete entities outside active area (iterate backwards)
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(cameraX, cameraY, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(enemyObjs) - 1, -1, -1):
            if isOutsideActiveArea(cameraX, cameraY, enemyObjs[i]):
                del enemyObjs[i]

        # add more entities to the active area, if we don't have enough
        # todo: instead of deleteing entities, we could just pool them
        # todo: reset them back into the active area with a new param permutation
        while len(grassObjs) < NUM_GRASS:
            grassObjs.append(makeGrass(cameraX, cameraY))
        while len(enemyObjs) < NUM_ENEMIES:
            enemyObjs.append(makeEnemy(cameraX, cameraY))

        # adjust camera
        # todo: replace with vector math and oop objects
        playerCenterX = playerObj['x'] + int(playerObj['size'] / 2)
        playerCenterY = playerObj['y'] + int(playerObj['size'] / 2)

        if (cameraX + WINDOW_CENTER[0]) - playerCenterX > CAMERA_DEATH_ZONE:
            cameraX = playerCenterX + CAMERA_DEATH_ZONE - WINDOW_CENTER[0]
        elif playerCenterX - (cameraX + WINDOW_CENTER[0]) > CAMERA_DEATH_ZONE:
            cameraX = playerCenterX - CAMERA_DEATH_ZONE - WINDOW_CENTER[0]

        if (cameraY + WINDOW_CENTER[1]) - playerCenterY > CAMERA_DEATH_ZONE:
            cameraY = playerCenterY + CAMERA_DEATH_ZONE - WINDOW_CENTER[1]
        elif playerCenterY - (cameraY + WINDOW_CENTER[1]) > CAMERA_DEATH_ZONE:
            cameraY = playerCenterY - CAMERA_DEATH_ZONE - WINDOW_CENTER[1]

        # draw green background
        DISPLAY_SURFACE.fill(GRASS_COLOR)

        # draw grass
        for gObj in grassObjs:
            gRect = pygame.Rect(gObj['x'] - cameraX, gObj['y'] - cameraY, gObj['width'], gObj['height'])
            DISPLAY_SURFACE.blit(GRASS_IMAGES[gObj['grassImage']], gRect)

        # draw enemies
        for eObj in enemyObjs:
            eObj['rect'] = pygame.Rect(eObj['x'] - cameraX,
                                       eObj['y'] - cameraY - getBounceAmount(eObj['bounce'], eObj['bounceRate'], eObj['bounceHeight']),
                                       gObj['width'],
                                       gObj['height'])
            DISPLAY_SURFACE.blit(eObj['surface'], eObj['rect'])

        # draw player
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect(playerObj['x'] - cameraX,
                                       playerObj['y'] - cameraY - getBounceAmount(playerObj['bounce'], BOUNCE_RATE, BOUNCE_HEIGHT),
                                       playerObj['size'],
                                       playerObj['size'])
            DISPLAY_SURFACE.blit(playerObj['surface'], playerObj['rect'])

        # draw health meter
        drawHealthMeter(playerObj['health'])

        # process events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] == RIGHT: # flip player image
                        playerObj['surface'] = pygame.transform.scale(AVATAR_L_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] == LEFT: # flip player image
                        playerObj['surface'] = pygame.transform.scale(AVATAR_R_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == K_r:
                    return  # restarts the game

                # keyup user no longer wants to move
                elif event.type == KEYUP:
                    if event.key in (K_UP, K_w):
                        moveUp = False
                    if event.key in (K_DOWN, K_s):
                        moveDown = False
                    if event.key in (K_LEFT, K_a):
                        moveLeft = False
                    if event.key in (K_RIGHT, K_d):
                        moveRight = False
                    if event.key == K_ESCAPE:
                        terminate()

        # update player
        if not gameOverMode:
            if moveLeft:
                playerObj['x'] -= MOVE_RATE
            if moveRight:
                playerObj['x'] += MOVE_RATE
            if moveUp:
                playerObj['y'] -= MOVE_RATE
            if moveDown:
                playerObj['y'] += MOVE_RATE

            # update bounce on move:
            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCE_RATE:
                playerObj['bounce'] = 0  # reset bounce amount

            # check if the player has collided with an enemy
            for i in range(len(enemyObjs) - 1, -1, -1):
                eObj = enemyObjs[i]
                if 'rect' in eObj and playerObj['rect'].colliderect(eObj['rect']):
                    if eObj['width'] * eObj['height'] <= playerObj['size']**2:
                        # player is larger, destroy enemy
                        playerObj['size'] += 1 + int((eObj['width'] * eObj['height'])**0.2)
                        del enemyObjs[i]

                        # update player image
                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(AVATAR_L_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(AVATAR_R_IMG, (playerObj['size'], playerObj['size']))

                        # check if we have won
                        if playerObj['size'] > WIN_SIZE:
                            winMode = True

                    # enemy is bigger --> take damage
                    elif not invulnerableMode:
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True
                            gameOverStartTime = time.time()

        # game over we lost
        else:
            DISPLAY_SURFACE.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAME_OVER_TIME:
                return # end the current game

        # check if we have won
        if winMode:
            DISPLAY_SURFACE.blit(winSurf, winRect)
            DISPLAY_SURFACE.blit(win2Surf, win2Rect)

        # draw to screen
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # red health bars
        pygame.draw.rect(DISPLAY_SURFACE, RED, (15, 5 + (10 * MAX_HEALTH - i * 10), 20, 10))
    for i in range(MAX_HEALTH): # white outline
        pygame.draw.rect(DISPLAY_SURFACE, WHITE, (15, 5 + (10 * MAX_HEALTH - i * 10), 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    """ returns the number of pixels to offset based on the bounce
    larger bounceRate means a slower bounce
    larger bounceHeight means a higher bounce
    currentBounce will always be less than bounceRate
    """
    return int(math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight)


def getRandomVelocity():
    speed = random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPosition(cameraX, cameraY, objWidth, objHeight):
    cameraRect = pygame.Rect(cameraX, cameraY, WINDOW_WIDTH, WINDOW_HEIGHT)
    while True:
        x = random.randint(cameraX - WINDOW_WIDTH, cameraX + (2 * WINDOW_WIDTH))
        y = random.randint(cameraY - WINDOW_HEIGHT, cameraY + (2 * WINDOW_HEIGHT))

        # create a rect of these random coords
        # then check against the camera rect to make sure that it's outside of view
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeEnemy(cameraX, cameraY):
    o = {}
    generalSize = random.randint(0, 25)
    multiplier = random.randint(1, 3)
    o['width'] = (generalSize + random.randint(0, 10)) * multiplier
    o['height'] = (generalSize + random.randint(0, 10)) * multiplier
    o['x'], o['y'] = getRandomOffCameraPosition(cameraX, cameraY, o['width'], o['height'])
    o['moveY'] = getRandomVelocity()
    o['moveX'] = getRandomVelocity()
    if o['moveX'] < 0: # facing left
        o['surface'] = pygame.transform.scale(AVATAR_L_IMG, (o['width'], o['height']))
    else:
        o['surface'] = pygame.transform.scale(AVATAR_R_IMG, (o['width'], o['height']))
    o['bounce'] = 0
    o['bounceRate'] = random.randint(10, 18)
    o['bounceHeight'] = random.randint(10, 50)
    return o


def makeGrass(cameraX, cameraY):
    g = {}
    g['grassImage'] = random.randint(0, len(GRASS_IMAGES) - 1)
    g['width'] = GRASS_IMAGES[g['grassImage']].get_width()
    g['height'] = GRASS_IMAGES[g['grassImage']].get_height()
    g['x'], g['y'] = getRandomOffCameraPosition(cameraX, cameraY, g['width'], g['height'])
    g['rect'] = pygame.Rect(g['x'], g['y'], g['width'], g['height'])
    return g


def isOutsideActiveArea(cameraX, cameraY, obj):
    """ returns False if cameraX and cameraY are more than
    a half-window length beyond the edge of the window
    """
    boundsLeftEdge = cameraX - WINDOW_WIDTH
    boundsTopEdge = cameraY - WINDOW_HEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINDOW_WIDTH * 3, WINDOW_HEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()