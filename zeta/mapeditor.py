import pygame
import resources as R

pygame.init()

screen = pygame.display.set_mode((640,480))
font = pygame.font.SysFont("Free Sans", 16)

map = []
for i in range(0,448,32):
    row = []
    for j in range(0,640,32):
        row.append(0)
    map.append(row)

#map = R.MAPS[32]

brush_size = 0
tile = 1
option = 0
while True:
    pygame.event.pump()
    for i in pygame.event.get():
        if i.type == pygame.KEYDOWN:
            if i.key in range(48,58):
                if option == 0:
                    brush_size = int(chr(i.key))
                else:
                    tile = int(chr(i.key))
                    if tile > 8:
                        tile = 1
            if i.key == pygame.K_b:
                option = 0
            if i.key == pygame.K_t:
                option = 1
            if i.key == pygame.K_s:
                print map
    if pygame.mouse.get_pressed()[0]:
        if not brush_size:
            if pygame.mouse.get_pos()[1]/32 < 14:
                map[pygame.mouse.get_pos()[1]/32][pygame.mouse.get_pos()[0]/32] = tile
        for j in range(-brush_size,brush_size):
            for k in range(-brush_size,brush_size):
                if j+pygame.mouse.get_pos()[1]/32 < 14 and j+pygame.mouse.get_pos()[1]/32 >= 0:
                    if k+pygame.mouse.get_pos()[0]/32 < 20 and k+pygame.mouse.get_pos()[0]/32 >= 0:
                        map[j+pygame.mouse.get_pos()[1]/32][k+pygame.mouse.get_pos()[0]/32] = tile
    
    screen.fill((128,128,128))
    
    iterate = 0
    jterate = 0
    for i in map:
        for j in i:
            if j == 1:
                screen.blit(R.IMAGES["tile-red.png"],(jterate*32,iterate*32))
            if j == 2:
                screen.blit(R.IMAGES["flyertile.png"],(jterate*32,iterate*32))
            if j == 3:
                screen.blit(R.IMAGES["walkertile.png"],(jterate*32,iterate*32))
            if j == 4:
                screen.blit(R.IMAGES["bouncetile.png"],(jterate*32,iterate*32))
            if j == 5:
                screen.blit(R.IMAGES["checkpointtile.png"],(jterate*32,iterate*32))
            if j == 6:
                screen.blit(R.IMAGES["spike.png"],(jterate*32,iterate*32))
            if j == 7:
                screen.blit(R.IMAGES["quicksand-red.png"],(jterate*32,iterate*32))
            if j == 8:
                screen.blit(R.IMAGES["coin.png"],(jterate*32,iterate*32))
            jterate += 1
        jterate = 0
        iterate += 1
    
    if option == 0:
        screen.blit(font.render("B to change brush size, T to change tile. Currently on B",1,(0,0,0)),(20,450))
    else:
        screen.blit(font.render("B to change brush size, T to change tile. Currently on T",1,(0,0,0)),(20,450))
    
    pygame.display.flip()