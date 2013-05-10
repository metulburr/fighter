import pygame
import sys
import math
import random

def image_from_url(url):
    try:
        from urllib2 import urlopen
        from cStringIO import StringIO as inout
    except ImportError:
        from urllib.request import urlopen
        from io import BytesIO as inout
    myurl = urlopen(url)
    return inout(myurl.read())

class Projectile:
    limit = 3
    def __init__(self, loc, color):
        self.surf = pygame.Surface((5,10)).convert()
        self.surf.set_colorkey((255,0,255))
        self.surf.fill(color)
        self.rect = self.surf.get_rect()
        self.rect.center = loc
        self.mask = pygame.mask.from_surface(self.surf)
        self.speed = 8

class Enemy:
    count = 3
    def __init__(self, start_loc, orig_image):
        self.score_value = 100
        self.orig_image = orig_image
        #link = 'http://i1297.photobucket.com/albums/ag23/metulburr/spaceship_enemy3_zpscfeb13bf.png'
        #self.orig_image = pygame.image.load(image_from_url(link)).convert()
        self.orig_image = pygame.transform.scale(self.orig_image, (40,80))
        self.orig_image.set_colorkey((255,0,255))
        self.image = pygame.transform.rotate(self.orig_image, 180)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = start_loc
        self.bullets = []
        self.speed = 2
        self.is_hit = False
        self.range_to_fire = False
        self.timestamp = pygame.time.get_ticks()
        self.distance_above_player = 200 #enemy to go above player to shootat player
        self.bullet_color = (255,0,0)
        
    def pos_towards_player(self, player_rect):
        '''get new coords towards player'''
        
        c = math.sqrt((player_rect.x - self.rect[0]) ** 2 + (player_rect.y - self.distance_above_player  - self.rect[1]) ** 2)
        try:
            x = (player_rect.x - self.rect[0]) / c
            y = ((player_rect.y - self.distance_above_player)  - self.rect[1]) / c
        except ZeroDivisionError:
            return False
        return (x,y)
        
    def update(self, player):
        if player.active:
            if not self.is_hit:
                #move enemy towards player
                new_pos = self.pos_towards_player(player.rect)
                if new_pos: #if not ZeroDivisonError 
                    self.rect.x, self.rect.y = (self.rect.x + new_pos[0] * self.speed, self.rect.y + new_pos[1] * self.speed)
        
    
        self.fire_update(player)
        if self.range_to_fire:  
            diff = pygame.time.get_ticks() - self.timestamp
            if diff > 1500.0:
                self.timestamp = pygame.time.get_ticks()
                if player.active: #if player is not dead
                    self.bullets.append(Projectile(self.rect.center, self.bullet_color))
        
    def fire_update(self, player):
        #if player is lower than enemy
        if player.rect.y >= self.rect.y: 
            try:
                offset_x =  self.rect.x - player.rect.x
                offset_y =  self.rect.y - player.rect.y
                d = int(math.degrees(math.atan(offset_x / offset_y)))
            except ZeroDivisionError:
                #player is above enemy
                return
            #if player is within 15 degrees lower of enemy
            if math.fabs(d) <= 15: 
                self.range_to_fire = True
            else:
                self.range_to_fire = False
                #self.bullets.append(Projectile(self.rect.center))
            


class Player:
    def __init__(self, start_loc):
        self.score = 0
        self.damage = 10
        self.active = True #check for end of game
        self.bullet_color = (255,255,255)
        
        self.speed = 4

        link = 'http://i1297.photobucket.com/albums/ag23/metulburr/spaceship2_zps095c332a.png'
        self.orig_image = pygame.image.load(image_from_url(link)).convert()
        self.orig_image = pygame.transform.scale(self.orig_image, (40,80))
        self.orig_image.set_colorkey((255,0,255))

        self.image = pygame.transform.rotate(self.orig_image, 180)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = start_loc

        self.bullets = []

    def move(self, x, y):
        if self.active:
            self.rect[0] += x * self.speed
            self.rect[1] += y * self.speed
            
    def update(self):
        if self.damage < 0:
            self.damage = 0
            self.active = False


class Control:
    def __init__(self):
        pygame.init()
        self.screensize = (800,600)
        self.screen = pygame.display.set_mode(self.screensize)
        self.screenrect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.player = Player((0,600))
        #self.enemy = Enemy((800,0))
        self.score_loss_per_shot = 25
        link = 'http://i1297.photobucket.com/albums/ag23/metulburr/spaceship_enemy3_zpscfeb13bf.png'
        self.enemy_image = pygame.image.load(image_from_url(link)).convert()
        self.enemies = []

        self.mainloop()
        
    def write(self, displaytext, color=(0,0,0), size=15, ul=False, bold=False,
            ital=False, font='timesnewroman'):
        font = pygame.font.SysFont(font, size)
        font.set_underline(ul)
        font.set_bold(bold)
        font.set_italic(ital)
        label = font.render(displaytext, 1, color)
        label_rect = label.get_rect()
        return label,label_rect

    def mainloop(self):
        run = True
        while run:
            self.screen.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if len(self.player.bullets) <= Projectile.limit:
                            self.player.score -= self.score_loss_per_shot
                            self.player.bullets.append(Projectile(self.player.rect.center, self.player.bullet_color))

            self.update()
            pygame.display.flip()
            self.clock.tick(60)

    def update(self):
        self.keys = pygame.key.get_pressed()
        
        self.player.update()
        self.player.rect.clamp_ip(self.screenrect) #make sure rect does not go outside of screen
        
        if len(self.enemies) <= Enemy.count:
            self.enemies.append(Enemy((random.randint(1,800),-100), self.enemy_image))

        if self.player.bullets:
            for obj in self.player.bullets[:]:
                self.screen.blit(obj.surf, obj.rect)
                obj.rect[1] -= obj.speed

                #did obj move off screen
                if obj.rect[1] < 0:
                    self.player.bullets.remove(obj)
                
                for enem in self.enemies[:]:
                    #did obj hit enemy rect
                    if obj.rect.colliderect(enem.rect):
                        offset_x =  enem.rect.x - obj.rect.x
                        offset_y =  enem.rect.y - obj.rect.y
                        #did object hit enemy mask
                        if obj.mask.overlap(enem.mask, (offset_x, offset_y)):
                            self.player.bullets.remove(obj)
                            self.enemies.remove(enem)
                            enem.is_hit = True
                            self.player.score += enem.score_value
                            break
                        #break
                        
        
        for enem in self.enemies:
            if enem.bullets:
                for obj in enem.bullets[:]:
                    self.screen.blit(obj.surf, obj.rect)
                    obj.rect[1] += obj.speed
                    offset_x =  obj.rect.x - self.player.rect.x 
                    offset_y =  obj.rect.y - self.player.rect.y
                    #did object hit player
                    if self.player.mask.overlap(obj.mask, (offset_x, offset_y)):
                        self.player.damage -= 1
                        enem.bullets.remove(obj)
                        break

    
        if self.keys[pygame.K_UP]:
            self.player.move(0,-1)
        if self.keys[pygame.K_DOWN]:
            self.player.move(0,1)
        if self.keys[pygame.K_RIGHT]:
            self.player.move(1,0)
        if self.keys[pygame.K_LEFT]:
            self.player.move(-1,0)
       
        
        for obj in self.enemies:
            obj.update(self.player)
            if not obj.is_hit:
                self.screen.blit(obj.image, obj.rect)
            
            #if player collides with enemy
            offset_x =  obj.rect.x - self.player.rect.x
            offset_y =  obj.rect.y - self.player.rect.y
            if self.player.mask.overlap(obj.mask, (offset_x, offset_y)):
                obj.is_hit = True
                self.player.damage -= 1
                self.player.score -= obj.score_value
                self.enemies.remove(obj)
                break


        self.screen.blit(self.player.image, self.player.rect)
        scoreboard = self.write('Score: {}'.format(self.player.score), color=(255,255,255), size=30)
        self.screen.blit(scoreboard[0], (10,10))

        if self.player.active:
            lifeboard = self.write('Damage: {}'.format(self.player.damage), color=(255,255,255), size=30)
            self.screen.blit(lifeboard[0], (self.screensize[0] - 150, 10))
        else:
            game_over = self.write('GAME OVER', color=(255,255,255), size=50)
            game_over[1].center = (self.screensize[0] // 2, self.screensize[1] // 2)
            self.screen.blit(game_over[0], game_over[1])
        

app = Control()
pygame.quit()
sys.exit()
