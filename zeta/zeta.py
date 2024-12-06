import pygame,sys,os,time
import resources as R

pygame.init()
pygame.mixer.pre_init()
pygame.mixer.init()

class Player:
    def __init__(self):
        self.sector = [7,4]
        self.current_sector = [7,4]
        self.pos = [128,192]
        self.rect = pygame.Rect(list(self.pos),(32,63))
        self.state = "Walker"
        
        self.speedx = 0
        self.speedy = 0
        self.vjump = 0
        
        self.deaths = 0
        self.coins = 0
        
        self.acceleration = 2
        self.direction = ""
        
        self.clock = pygame.time.Clock()
        
        self.timer = 0
    
    def get_rect(self):
        return self.rect
    
    def blit(self,screen):
        if self.state == "Walker":
            if not self.direction:
                screen.blit(R.IMAGES["walker.png"],self.rect.topleft)
            else:
                screen.blit(R.IMAGES["walker-"+self.direction+str(int(self.timer%4)+1)+".png"],self.rect.topleft)
            self.direction = ""
        else:
            screen.blit(R.IMAGES["flyer-"+str(int(self.timer%2)+1)+".png"],self.rect.topleft)
    
    def move(self,direction,up=-1):
        if direction != -1:
            if not direction:
                self.speedx = -8
                self.direction = "l"
            if direction:
                self.speedx = 8
                self.direction = "r"
        if self.state == "Flyer":
            if up != -1:
                if not up:
                    self.speedy = -8
                if up:
                    self.speedy = 8
    
    def jump(self,amount=-15):
        if self.state != "Flyer":
            self.vjump = amount
    
    def tick(self,collides):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 4/self.clock.get_fps()
        
        if self.speedy > 20:
            self.speedy = 20
        if self.speedy < 0 and "top" not in collides and self.state == "Flyer":
            self.rect.top += self.speedy
        if "bottom" in collides and self.vjump:
            self.speedy = self.vjump
            play_sound("jump.wav")
        if self.state != "Flyer":
            self.speedy += 1
        if self.speedy > 0 and "bottom" not in collides:
            self.rect.top += self.speedy
        if self.speedy < 0 and "top" not in collides and self.state == "Walker":
            self.rect.top += self.speedy
        if self.state == "Flyer":
            self.speedy = 0
        if "right" not in collides and self.speedx > 0:
            self.rect.left += self.speedx
        if "left" not in collides and self.speedx < 0:
            self.rect.left += self.speedx
        
        #if self.state != "Flyer":
        self.speedx = 0
        if self.state == "Flyer":
            self.speedy = 0
        self.vjump = 0
    
    def set_map(self,map):
        self.map = map
    
    def mutate(self,type):
        vtime = time.time()
        if type != self.state:
            play_sound("mutate.wav")
        if type == "Flyer" and self.state != type:
            self.state = "Flyer"
            self.rect.height = 31
        if type == "Walker" and self.state != type:
            self.state = "Walker"
            self.rect.height = 63
    
    def set_sector(self,sector):
        self.current_sector = sector
    
    def get_sector(self):
        return self.sector
    
    def save(self,checkpoint):
        self.sector = self.current_sector
        self.pos = list([checkpoint.left,checkpoint.top-32])
    
    def kill(self):
        self.rect.topleft = list(self.pos)
        self.speedx = 0
        self.speedy = 0
        self.deaths += 1
        play_sound("die.wav")
    
    def add_coin(self):
        self.coins += 1
        play_sound("coin.wav")
    
    def get_deaths(self):
        return self.deaths
    
    def get_coins(self):
        return self.coins

class Tile:
    def __init__(self,pos,colour):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = R.IMAGES["tile-"+colour+".png"]
        self.type = "Tile"
    
    def get_rect(self):
        return self.rect
    
    def blit(self,screen):
        screen.blit(self.image,self.rect)
    
    def change_colour(self,colour):
        self.image = R.IMAGES["tile-"+colour+".png"]

class QuicksandTile(Tile):
    def __init__(self,pos,colour):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = pygame.Surface((32,32))
        self.image.blit(R.IMAGES["quicksand-"+colour+".png"],(0,0))
        self.type = "Quicksand"
        self.touched = False
        self.exist = 20
    
    def set_touched(self,touched):
        self.touched = touched
    
    def get_rect(self):
        if self.exist:
            return self.rect
        else:
            return pygame.Rect(0,0,0,0)
    
    def blit(self,screen):
        if self.touched and self.exist:
            self.image.set_alpha(255.0/(21-self.exist))
            self.exist -= 1
            if self.exist <= 0:
                play_sound("quicksand.wav")
        if not self.touched:
            self.exist = 20
            self.image.set_alpha(255)
        if self.exist:
            screen.blit(self.image,self.rect)

class FlyerTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = R.IMAGES["flyertile.png"]
        self.type = "Flyer"

class WalkerTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = R.IMAGES["walkertile.png"]
        self.type = "Walker"

class BounceTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = R.IMAGES["bouncetile.png"]
        self.type = "Bounce"

class CheckPointTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect(pos,(32,32))
        self.image = R.IMAGES["checkpointtile.png"]
        self.type = "Checkpoint"

class SpikeTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect((pos[0]+1,pos[1]+1),(30,30))
        self.image = R.IMAGES["spike.png"]
        self.type = "Spike"

class ConveyorTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect((pos[0],pos[1]),(32,32))
        self.image = R.IMAGES["conveyor.png"]
        self.type = "Conveyor"

class CoinTile(Tile):
    def __init__(self,pos):
        self.rect = pygame.Rect((pos[0]+1,pos[1]+1),(30,30))
        self.image = R.IMAGES["coin.png"]
        self.type = "Coin"
        self.exist = True
    
    def touch(self):
        self.exist = False
    
    def get_rect(self):
        if self.exist:
            return self.rect
        else:
            return pygame.Rect(0,0,0,0)
    
    def blit(self,screen):
        if self.exist:
            screen.blit(self.image,self.rect)

class Map:
    def initialise(self):     
        self.map_tiles = []
        iterate = 0
        jterate = 0
        for i in self.map:
            for j in i:
                if j == 1:
                    self.map_tiles.append(Tile((32*jterate,32*iterate),self.colour))
                if j == 2:
                    self.map_tiles.append(FlyerTile((32*jterate,32*iterate)))
                if j == 3:
                    self.map_tiles.append(WalkerTile((32*jterate,32*iterate)))
                if j == 4:
                    self.map_tiles.append(BounceTile((32*jterate,32*iterate)))
                if j == 5:
                    self.map_tiles.append(CheckPointTile((32*jterate,32*iterate)))
                if j == 6:
                    self.map_tiles.append(SpikeTile((32*jterate,32*iterate)))
                if j == 7:
                    self.map_tiles.append(QuicksandTile((32*jterate,32*iterate),self.colour))
                if j == 8:
                    self.map_tiles.append(CoinTile((32*jterate,32*iterate)))
                if j == 9:
                    self.map_tiles.append(ConveyorTile((32*jterate,32*iterate)))
                jterate += 1
            jterate = 0
            iterate += 1
        
        self.font = pygame.font.SysFont("Free Sans",24)
    
    def set_player(self,player):
        self.player = player
    
    def blit(self,screen):
        for i in self.map_tiles:
            i.blit(screen)
        pygame.draw.rect(screen,(255,255,255),(0,448,640,32))
        screen.blit(self.font.render(self.name,1,(0,0,0)),(318-self.font.size(self.name)[0]/2,448))
        screen.blit(self.font.render(self.name,1,(255,255,255)),(320-self.font.size(self.name)[0]/2,450))
        
        screen.blit(self.font.render("Coins: "+str(self.player.get_coins())+"/"+str(R.coin_count),1,(0,0,0)),(8,448))
        screen.blit(self.font.render("Coins: "+str(self.player.get_coins())+"/"+str(R.coin_count),1,(255,255,255)),(10,450))
        
        screen.blit(self.font.render("Deaths: "+str(self.player.get_deaths()),1,(0,0,0)),(488,448))
        screen.blit(self.font.render("Deaths: "+str(self.player.get_deaths()),1,(255,255,255)),(490,450))
    
    def reset(self,player):
        for i in self.map_tiles:
            if i.type == "Quicksand":
                i.set_touched(False)
    
    def tick(self,player):
        pass
    
    def check_collides(self,player):
        collided = ""
        kill = False
        move = False
        for j in self.map_tiles:
            if j.type == "Spike":
                if j.get_rect().colliderect(player.get_rect()):
                    player.kill()
                    kill = True
                    return collided,kill
            if j.type == "Tile":
                i = j.get_rect()
                player.get_rect().move_ip(0,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().bottom >= i.top and player.get_rect().top <= i.top:
                        collided += "bottom"
                        player.get_rect().bottom = i.top+1
                player.get_rect().move_ip(0,-2)
                if player.get_rect().colliderect(i):
                    if player.get_rect().top <= i.bottom and player.get_rect().bottom >= i.bottom:
                        collided += "top"
                        player.get_rect().top = i.bottom
                player.get_rect().move_ip(1,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().right >= i.left and player.get_rect().left <= i.left:
                        collided += "right"
                        player.get_rect().right = i.left+1
                player.get_rect().move_ip(-2,0)
                if player.get_rect().colliderect(i):
                    if player.get_rect().left <= i.right and player.get_rect().right >= i.right:
                        collided += "left"
                        player.get_rect().left = i.right-1
                player.get_rect().move_ip(1,0)
            if j.type == "Quicksand":
                i = j.get_rect()
                player.get_rect().move_ip(0,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().bottom >= i.top and player.get_rect().top <= i.top:
                        collided += "bottom"
                        player.get_rect().bottom = i.top+1
                        if player.state == "Walker":
                            j.set_touched(True)
                player.get_rect().move_ip(0,-2)
                if player.get_rect().colliderect(i):
                    if player.get_rect().top <= i.bottom and player.get_rect().bottom >= i.bottom:
                        collided += "top"
                        player.get_rect().top = i.bottom
                player.get_rect().move_ip(1,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().right >= i.left and player.get_rect().left <= i.left:
                        collided += "right"
                        player.get_rect().right = i.left+1
                player.get_rect().move_ip(-2,0)
                if player.get_rect().colliderect(i):
                    if player.get_rect().left <= i.right and player.get_rect().right >= i.right:
                        collided += "left"
                        player.get_rect().left = i.right-1
                player.get_rect().move_ip(1,0)
            if j.type == "Conveyor":
                i = j.get_rect()
                player.get_rect().move_ip(0,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().bottom >= i.top and player.get_rect().top <= i.top:
                        collided += "bottom"
                        player.get_rect().bottom = i.top+1
                        if player.speedx == 8:
                            player.speedx = 8
                        if player.speedx == 0:
                            player.speedx = 4
                        if player.speedx == -8:
                            player.speedx = -4
                player.get_rect().move_ip(0,-2)
                if player.get_rect().colliderect(i):
                    if player.get_rect().top <= i.bottom and player.get_rect().bottom >= i.bottom:
                        collided += "top"
                        player.get_rect().top = i.bottom
                player.get_rect().move_ip(1,1)
                if player.get_rect().colliderect(i):
                    if player.get_rect().right >= i.left and player.get_rect().left <= i.left:
                        collided += "right"
                        player.get_rect().right = i.left+1
                player.get_rect().move_ip(-2,0)
                if player.get_rect().colliderect(i):
                    if player.get_rect().left <= i.right and player.get_rect().right >= i.right:
                        collided += "left"
                        player.get_rect().left = i.right-1
                player.get_rect().move_ip(1,0)
            if j.type == "Flyer":
                if j.get_rect().colliderect(player.get_rect()):
                    player.mutate("Flyer")
            if j.type == "Walker":
                if j.get_rect().colliderect(player.get_rect()):
                    player.mutate("Walker")
            if j.type == "Bounce":
                if j.get_rect().colliderect(player.get_rect()):
                    player.jump(-40)
            if j.type == "Checkpoint":
                if j.get_rect().colliderect(player.get_rect()):
                    player.save(j.get_rect())
            if j.type == "Coin":
                if j.get_rect().colliderect(player.get_rect()):
                    player.add_coin()
                    j.touch()
        
        return collided,kill
    
    def push_up(self,player):
        for i in self.map_tiles:
            if i.type == "Tile" or i.type == "Quicksand" or i.type == "Conveyor":
                player.get_rect().move_ip(0,1)
                if player.get_rect().colliderect(i.get_rect()):
                    if player.get_rect().bottom >= i.get_rect().top and player.get_rect().top <= i.get_rect().top:
                        player.get_rect().bottom = i.get_rect().top+1
                player.get_rect().move_ip(0,-2)
                if player.get_rect().colliderect(i.get_rect()):
                    if player.get_rect().top <= i.get_rect().bottom and player.get_rect().bottom >= i.get_rect().bottom:
                        player.get_rect().top = i.get_rect().bottom
                        player.speedy = 0
                player.get_rect().move_ip(0,1)

class Map01(Map):
    def __init__(self):
        self.name = "Welcome to Zeta!"
        self.map = R.MAPS[0]
        
        self.colour = "yellow"
        
        self.initialise()
    
    def reset(self,player):
        if player.get_rect().top == 0:
            self.name = "Welcome Back!"
        
        Map.reset(self,player)

class Map02(Map):
    def __init__(self):
        self.name = "Who Says Robots Can't Fly?"
        self.map = R.MAPS[1]
        
        self.colour = "yellow"
        
        self.initialise()

class Map03(Map):
    def __init__(self):
        self.name = "The Parting of the Way"
        self.map = R.MAPS[2]
        
        self.colour = "yellow"
        
        self.initialise()

class Map04(Map):
    def __init__(self):
        self.name = "The Cellar"
        self.map = R.MAPS[3]
        
        self.colour = "yellow"
        
        self.initialise()

class Map05(Map):
    def __init__(self):
        self.name = "How Do You Get Up There?"
        self.map = R.MAPS[4]
        
        self.colour = "yellow"
        
        self.initialise()

class Map06(Map):
    def __init__(self):
        self.name = "Ventilation Shaft"
        self.map = R.MAPS[5]
        
        self.colour = "yellow"
        
        self.initialise()

class Map07(Map):
    def __init__(self):
        self.name = "Oops..."
        self.map = R.MAPS[6]
        
        self.colour = "yellow"
        
        self.initialise()

class Map08(Map):
    def __init__(self):
        self.name = "Think Fast!"
        self.map = R.MAPS[7]
        
        self.colour = "yellow"
        
        self.initialise()

class Map09(Map):
    def __init__(self):
        self.name = "Mountain to Climb"
        self.map = R.MAPS[8]
        
        self.colour = "green"
        
        self.initialise()

class Map10(Map):
    def __init__(self):
        self.name = "Grave Digger"
        self.map = R.MAPS[9]
        
        self.colour = "green"
        
        self.initialise()

class Map11(Map):
    def __init__(self):
        self.name = "Mine shaft"
        self.map = R.MAPS[10]
        
        self.colour = "green"
        
        self.initialise()

class Map12(Map):
    def __init__(self):
        self.name = "Z"
        self.map = R.MAPS[11]
        
        self.colour = "green"
        
        self.initialise()

class Map13(Map):
    def __init__(self):
        self.name = "Junk Removal"
        self.map = R.MAPS[12]
        
        self.colour = "yellow"
        
        self.initialise()

class Map14(Map):
    def __init__(self):
        self.name = "Spring Along Now!"
        self.map = R.MAPS[13]
        
        self.colour = "yellow"
        
        self.initialise()

class Map15(Map):
    def __init__(self):
        self.name = "...And Back Again"
        self.map = R.MAPS[14]
        
        self.colour = "yellow"
        
        self.initialise()

class Map16(Map):
    def __init__(self):
        self.name = "Speech Bubble"
        self.map = R.MAPS[15]
        
        self.colour = "red"
        
        self.initialise()

class Map17(Map):
    def __init__(self):
        self.name = "The Only Way is Up"
        self.map = R.MAPS[16]
        
        self.colour = "red"
        
        self.initialise()

class Map18(Map):
    def __init__(self):
        self.name = "Falling Platforms"
        self.map = R.MAPS[17]
        
        self.colour = "red"
        
        self.initialise()

class Map19(Map):
    def __init__(self):
        self.name = "Syntax Error"
        self.map = R.MAPS[18]
        
        self.colour = "green"
        
        self.initialise()

class Map20(Map):
    def __init__(self):
        self.name = "To Change or Not to Change?"
        self.map = R.MAPS[19]
        
        self.colour = "red"
        
        self.initialise()

class Map21(Map):
    def __init__(self):
        self.name = "Alice in Spikeland"
        self.map = R.MAPS[20]
        
        self.colour = "red"
        
        self.initialise()

class Map22(Map):
    def __init__(self):
        self.name = "Round the Bend!"
        self.map = R.MAPS[21]
        
        self.colour = "red"
        
        self.initialise()

class Map23(Map):
    def __init__(self):
        self.name = "Graveyard"
        self.map = R.MAPS[22]
        
        self.colour = "red"
        
        self.initialise()

class Map24(Map):
    def __init__(self):
        self.name = "Dead End"
        self.map = R.MAPS[23]
        
        self.colour = "red"
        
        self.initialise()

class Map25(Map):
    def __init__(self):
        self.name = "Windows XP"
        self.map = R.MAPS[24]
        
        self.colour = "green"
        
        self.initialise()

class Map26(Map):
    def __init__(self):
        self.name = "Minefield"
        self.map = R.MAPS[25]
        
        self.colour = "green"
        
        self.initialise()

class Map27(Map):
    def __init__(self):
        self.name = "Turn Back"
        self.map = R.MAPS[26]
        
        self.colour = "green"
        
        self.initialise()

class Map28(Map):
    def __init__(self):
        self.name = "Eddie the Eagle"
        self.map = R.MAPS[27]
        
        self.colour = "green"
        
        self.initialise()

class Map29(Map):
    def __init__(self):
        self.name = "Fly-O-Bot"
        self.map = R.MAPS[28]
        
        self.colour = "green"
        
        self.initialise()

class Map30(Map):
    def __init__(self):
        self.name = "Air Vent"
        self.map = R.MAPS[29]
        
        self.colour = "blue"
        
        self.initialise()

class Map31(Map):
    def __init__(self):
        self.name = "Trapdoors"
        self.map = R.MAPS[30]
        
        self.colour = "blue"
        
        self.initialise()

class Map32(Map):
    def __init__(self):
        self.name = "Chimney Sweep"
        self.map = R.MAPS[31]
        
        self.colour = "blue"
        
        self.initialise()

class Map33(Map):
    def __init__(self):
        self.name = "Logic"
        self.map = R.MAPS[32]
        
        self.colour = "green"
        
        self.initialise()

class Map34(Map):
    def __init__(self):
        self.name = "Bounce-A-Lot"
        self.map = R.MAPS[33]
        
        self.colour = "green"
        
        self.initialise()

class Map35(Map):
    def __init__(self):
        self.name = "Mining for Gold"
        self.map = R.MAPS[34]
        
        self.colour = "red"
        
        self.initialise()

class Map36(Map):
    def __init__(self):
        self.name = "Speed"
        self.map = R.MAPS[35]
        
        self.colour = "blue"
        
        self.initialise()

class Map37(Map):
    def __init__(self):
        self.name = "Mind your Head"
        self.map = R.MAPS[38]
        
        self.colour = "green"
        
        self.initialise()

class Map38(Map):
    def __init__(self):
        self.name = "Marshland"
        self.map = R.MAPS[36]
        
        self.colour = "green"
        
        self.initialise()

class Map39(Map):
    def __init__(self):
        self.name = "Turn to the Right"
        self.map = R.MAPS[37]
        
        self.colour = "blue"
        
        self.initialise()

class Map40(Map):
    def __init__(self):
        self.name = "Works Both Ways"
        self.map = R.MAPS[39]
        
        self.colour = "blue"
        
        self.initialise()

class Map41(Map):
    def __init__(self):
        self.name = "Up'n'Down"
        self.map = R.MAPS[40]
        
        self.colour = "blue"
        
        self.initialise()

class Map42(Map):
    def __init__(self):
        self.name = "Dodge 'em Spikes"
        self.map = R.MAPS[41]
        
        self.colour = "blue"
        
        self.initialise()

class Map43(Map):
    def __init__(self):
        self.name = "Ooh...Shiny!"
        self.map = R.MAPS[42]
        
        self.colour = "blue"
        
        self.initialise()

class Tut01(Map):
    def __init__(self):
        self.name = "Tutorial"
        self.map = R.tutorial[0]
        
        self.colour = "grey"
        
        self.font = pygame.font.SysFont("Free Sans",64)
        
        self.message = "Welcome to the Zeta tutorial!"
        
        self.timer = 0
        self.clock = pygame.time.Clock()
        
        self.initialise()
    
    def blit(self,screen):
        Map.blit(self,screen)
        
        screen.blit(self.font.render(self.message,1,(0,0,0)),(320-self.font.size(self.message)[0]/2,230))
    
    def reset(self,player):
        Map.reset(self,player)
        
        self.clock = pygame.time.Clock()
        self.timer = 0
        
        self.message = "Welcome to the Zeta tutorial!"
    
    def tick(self,player):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 1/self.clock.get_fps()
        
        if self.timer > 2:
            self.message = "Use the arrow keys to move"
        if self.timer > 4:
            self.message = "(WASD also works)"
        if self.timer > 6:
            self.message = "Go right to continue"

class Tut02(Map):
    def __init__(self):
        self.name = "Tutorial"
        self.map = R.tutorial[1]
        
        self.colour = "grey"
        
        self.font = pygame.font.SysFont("Free Sans",64)
        
        self.message = "Checkpoints save your progress"
        
        self.timer = 0
        self.clock = pygame.time.Clock()
        
        self.initialise()
    
    def blit(self,screen):
        Map.blit(self,screen)
        
        screen.blit(self.font.render(self.message,1,(0,0,0)),(320-self.font.size(self.message)[0]/2,230))
    
    def reset(self,player):
        Map.reset(self,player)
        
        self.clock = pygame.time.Clock()
        self.timer = 0
        
        self.message = "Checkpoints save your progress"
    
    def tick(self,player):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 1/self.clock.get_fps()
        
        if self.timer > 2:
            self.message = "When you die you return to them"
        if self.timer > 4:
            self.message = "You also return to normal state"
        if self.timer > 6:
            self.message = "Quicksand disolves if you touch it"
        if self.timer > 8:
            self.message = "Don't touch the spikes!"
        if self.timer > 10:
            self.message = "Press space to jump"
        if self.timer > 12:
            self.message = "Touch the spring to do a big jump!"
        

class Tut03(Map):
    def __init__(self):
        self.name = "Tutorial"
        self.map = R.tutorial[2]
        
        self.colour = "grey"
        
        self.font = pygame.font.SysFont("Free Sans",64)
        
        self.message = "Pillars change your state"
        
        self.timer = 0
        self.clock = pygame.time.Clock()
        
        self.initialise()
    
    def blit(self,screen):
        Map.blit(self,screen)
        
        screen.blit(self.font.render(self.message,1,(0,0,0)),(280-self.font.size(self.message)[0]/2,230))
    
    def reset(self,player):
        Map.reset(self,player)
        
        self.clock = pygame.time.Clock()
        self.timer = 0
        
        self.message = "Pillars change your state"
    
    def tick(self,player):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 1/self.clock.get_fps()
        
        if self.timer > 2:
            self.message = "F makes you a flyer"
        if self.timer > 4:
            self.message = "Use the arrows to move"
        if self.timer > 7:
            self.message = "W makes you normal again"

class Tut04(Map):
    def __init__(self):
        self.name = "Tutorial"
        self.map = R.tutorial[3]
        
        self.colour = "grey"
        
        self.font = pygame.font.SysFont("Free Sans",64)
        
        self.message = "If you ever get stuck, press K"
        
        self.timer = 0
        self.clock = pygame.time.Clock()
        
        self.initialise()
    
    def blit(self,screen):
        Map.blit(self,screen)
        
        screen.blit(self.font.render(self.message,1,(0,0,0)),(350-self.font.size(self.message)[0]/2,110))
    
    def reset(self,player):
        Map.reset(self,player)
        
        self.clock = pygame.time.Clock()
        self.timer = 0
        
        self.message = "If you ever get stuck, press K"
    
    def tick(self,player):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 1/self.clock.get_fps()
        
        if self.timer > 3:
            self.message = "This kills you so you go back to the last checkpoint"
        if self.timer > 5:
            self.message = "F for Fullscreen"
        if self.timer > 9:
            self.message = "Get all the coins to win"
        if self.timer > 11:
            self.message = "Start by touching this one"
        
        for i in self.map_tiles:
            if i.type == "Coin":
                if i.exist == False:
                    player.sector = [3,0]
                    player.current_sector = [3,0]
                    player.pos = [64,192]
                    player.rect.topleft = [64,192]
                    return [3,0]

class MapEE(Map):
    def __init__(self):
        self.name = "This room is a bug, please tell me if you find it"
        self.map = R.empty
        
        self.colour = "grey"
        
        self.initialise()

class MapWN(Map):
    def __init__(self,player):
        self.name = "YOU WIN!!!!!"
        self.map = R.win
        
        self.colours = ["yellow","red","green","blue","grey"]
        
        self.colour = self.colours[0]
        
        self.message = ""
        
        self.font = pygame.font.SysFont("Free Sans",64)
        self.sfont = pygame.font.SysFont("Free Sans",16)
        
        self.timer = 0
        self.clock = pygame.time.Clock()
        
        self.initialise()
    def tick(self,player):
        self.clock.tick()
        if self.clock.get_fps():
            self.timer += 1/self.clock.get_fps()
        
        for i in self.map_tiles:
            i.change_colour(self.colours[int(self.timer)%5])
        
        deaths = player.get_deaths()
        if player.get_deaths():
            self.message = "You win! Good job!"
        if player.get_deaths() < 1000:
            self.message = "You win! Nice one!"
        if player.get_deaths() < 500:
            self.message = "You win! Your getting good at this!"
        if player.get_deaths() < 100:
            self.message = "You win! Wow!"
        if player.get_deaths() < 50:
            self.message = "You win! Did you cheat!"
        if player.get_deaths() < 10:
            self.message = "You win! Incredible!"
    
    def blit(self,screen):
        Map.blit(self,screen)
        screen.blit(self.font.render(self.message,1,(0,0,0)),(320-self.font.size(self.message)[0]/2,350))
        screen.blit(self.sfont.render("Enter to return to world",1,(0,0,0)),(48,388))

class Main:
    def __init__(self):
        pygame.mixer.music.load(os.path.join("data","music","pyweek.wav"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.screen = pygame.display.set_mode((640,480))
        pygame.mouse.set_visible(False)
        self.image = pygame.Surface((640,480))
        self.player = Player()
        self.bigmap = [[Map39(),Map43(),Map42(),Map40(),           Map36(),Map41()],
                       [Map35(),Map21(),Map22(),Map23(),           Map24(),Map32()],
                       [Map20(),Map18(),Map17(),Map16(),           Map30(),Map31()],
                       [Map01(),Map02(),Map03(),Map05(),           Map06(),Map15()],
                       [Map34(),Map37(),Map04(),MapWN(self.player),Map07(),Map14()],
                       [Map33(),Map38(),Map10(),Map09(),           Map08(),Map13()],
                       [Map29(),Map12(),Map11(),Map25(),           Tut04(),Tut03()],
                       [Map28(),Map27(),Map19(),Map26(),           Tut01(),Tut02()]]
        
        self.fullscreen = 0
        self.won = False
        
        for i in self.bigmap:
            for j in i:
                j.set_player(self.player)
        self.map_sector = [7,4]
        self.font = pygame.font.SysFont("Free Sans",32)
        
        self.clock = pygame.time.Clock()
    
    def blit(self):
        self.image.fill((128,128,128))
        self.player.blit(self.image)
        self.bigmap[self.map_sector[0]][self.map_sector[1]].blit(self.image)
        
        if not self.fullscreen:
            self.screen.blit(self.image,(0,0))
        else:
            width = int(pygame.display.list_modes()[0][1]/480.0*640)
            self.screen.blit(pygame.transform.scale(self.image,(width,pygame.display.list_modes()[0][1])),(0,0))
        
        pygame.display.flip()
    
    def tick(self):
        arg = self.bigmap[self.map_sector[0]][self.map_sector[1]].tick(self.player)
        
        if arg:
            self.map_sector = arg
        
        if self.player.get_rect().left >= 632 and self.player.speedx > 0:
            self.map_sector[1] += 1
            self.player.get_rect().left = 0
            self.player.mutate("Walker")
            self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
        if self.player.get_rect().left <= 8 and self.player.speedx < 0:
            self.map_sector[1] -= 1
            self.player.get_rect().right = 640
            self.player.mutate("Walker")
            self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
        if self.player.get_rect().top >= 472 and self.player.speedy > 0:
            self.map_sector[0] += 1
            self.player.get_rect().top = 0
            self.player.mutate("Walker")
            self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
        if self.player.get_rect().bottom <= 8 and self.player.speedy < 0:
            self.map_sector[0] -= 1
            self.player.get_rect().bottom = 480
            self.player.mutate("Walker")
            self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
        self.player.set_sector(list(self.map_sector))
        collided,kill = self.bigmap[self.map_sector[0]][self.map_sector[1]].check_collides(self.player)
        if kill:
            self.map_sector = list(self.player.get_sector())
            self.player.mutate("Walker")
            self.player.speedy = 0
            self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
        self.player.tick(collided)
        self.bigmap[self.map_sector[0]][self.map_sector[1]].push_up(self.player)
        
        if self.player.get_coins() >= R.coin_count and not self.won:
            self.map_sector = [4,3]
            self.player.pos = [64,192]
            self.player.get_rect().topleft = [64,192]
            self.won = True
    
    def check_events(self):
        pygame.event.pump()
        for i in pygame.event.get():
            if i.type == pygame.KEYDOWN:
                if i.key in R.KEYS["jump"]:
                    self.player.jump()
                if i.key in R.KEYS["kill"]:
                    self.player.kill()
                    self.map_sector = list(self.player.get_sector())
                    self.player.mutate("Walker")
                    self.player.speedy = 0
                    self.bigmap[self.map_sector[0]][self.map_sector[1]].reset(self.player)
                if i.key in R.KEYS["quit"]:
                    sys.exit()
                if i.key in R.KEYS["return"]:
                    if self.map_sector == [4,3]:
                        self.map_sector = [3,0]
                        self.player.get_rect().topleft = [64,192]
                if i.key in R.KEYS["fullscreen"]:
                    self.fullscreen = 1-self.fullscreen
                    if self.fullscreen:
                        width = int(pygame.display.list_modes()[0][1]/480.0*640)
                        pygame.display.set_mode((width,pygame.display.list_modes()[0][1]))
                        pygame.display.toggle_fullscreen()
                    else:
                        pygame.display.set_mode((640,480))
            if i.type == pygame.QUIT:
                sys.exit()
        for i in R.KEYS["left"]:
            if pygame.key.get_pressed()[i]:
                self.player.move(0)
                break
        for i in R.KEYS["right"]:
            if pygame.key.get_pressed()[i]:
                self.player.move(1)
                break
        for i in R.KEYS["up"]:
            if pygame.key.get_pressed()[i]:
                self.player.move(-1,0)
                break
        for i in R.KEYS["down"]:
            if pygame.key.get_pressed()[i]:
                self.player.move(-1,1)
                break
    
    def run(self):
        while True:
            self.clock.tick(30)
            
            self.check_events()
            self.tick()
            self.blit()

def play_sound(sound, volume=0.25):
    R.SOUNDS[sound].play()

M = Main()
M.run()