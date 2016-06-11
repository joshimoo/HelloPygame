import sys
import pygame

from pygame.locals import *

# init pygame
pygame.init()

# load and play sound effect
soundObj = pygame.mixer.Sound('beepingsound.wav')
soundObj.play()

# load and play background music
pygame.mixer.music.load('backgroundmusic.mp3')
pygame.mixer.music.play(-1, 0.00)  # -1 => infinite loop

