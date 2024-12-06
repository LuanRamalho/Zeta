import pygame,os
from maps import *

pygame.init()

KEYS = {"jump"       : [pygame.K_j,pygame.K_w,pygame.K_x,pygame.K_SPACE,pygame.K_UP],
        "left"       : [pygame.K_a,pygame.K_LEFT],
        "right"      : [pygame.K_d,pygame.K_RIGHT],
        "up"         : [pygame.K_w,pygame.K_UP],
        "down"       : [pygame.K_s,pygame.K_DOWN],
        "quit"       : [pygame.K_q,pygame.K_ESCAPE],
        "fullscreen" : [pygame.K_f],
        "kill"       : [pygame.K_k],
        "return"     : [pygame.K_RETURN]}

IMAGES = {}
for i in os.listdir(os.path.join("data","art")):
    if i[-4:] == ".png":
        IMAGES[i] = pygame.image.load(os.path.join("data","art",i))

SOUNDS = {}
for i in os.listdir(os.path.join("data","sounds")):
    if i[-4:] == ".wav":
        SOUNDS[i] = pygame.mixer.Sound(os.path.join("data","sounds",i))
        SOUNDS[i].set_volume(0.5)

coin_count = 20