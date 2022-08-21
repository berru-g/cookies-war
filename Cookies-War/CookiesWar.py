#hack game cookies 22
from queue import Full
import pygame
from pygame.locals import *
from pygame import mixer
import os
import os.path
import time
import random
import math

#mixer.init()
#pygame.mixer.pre_init(44100,-16,2, 1024)
#mixer.music.load('synth.wav')
#mixer.music.play(-1)
#####################(-1)=loop infini du son

pygame.font.init()
#
WIDTH, HEIGHT = 1518, 767
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookies War")
icon=pygame.image.load('icon2.png')
pygame.display.set_icon(icon)

# Load images
EDGE = pygame.image.load(os.path.join("assets", "edge.png"))
CHROME = pygame.image.load(os.path.join("assets", "chrome.png"))
FIREFOX = pygame.image.load(os.path.join("assets", "firefox.png"))

# Player player
HERO = pygame.image.load(os.path.join("assets", "tor.png"))

# Lasers
COOKIE1 = pygame.image.load(os.path.join("assets", "cookie.png"))
COOKIE2 = pygame.image.load(os.path.join("assets", "cookie2.png"))
COOKIE3 = pygame.image.load(os.path.join("assets", "cookie3.png"))
ARME = pygame.image.load(os.path.join("assets", "serrure.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fond.png")), (WIDTH, HEIGHT))
#BG2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black2.png")), (WIDTH, HEIGHT))


#############################################
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30
    SPEED = 20
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
#            bulletSound=mixer.Sound('laser.wav')

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=500):
        super().__init__(x, y, health)
        self.ship_img = HERO
        self.laser_img = ARME
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (EDGE, COOKIE1),
                "green": (CHROME, COOKIE2),
                "blue": (FIREFOX, COOKIE3)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 200
    level = 0
    winner = 3
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        ##############
        
        WIN.blit(lives_label, (0, 0))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
            
            player.draw(WIN)
        #################################################  
        if level == winner:
            lost_label = lost_font.render("You Win !!", 1, (255,255,255))  
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        pygame.display.update()
    #while run:
        #clock.tick(FPS)
#        redraw_window()
        ##########################################################################
        if lost:
            lost_label = lost_font.render("You Loose!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
#changement de background a chaque level
#BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        #if lives == 5 and player.health >= 3:
#            lost_label = lost_font.render("You Win ", 4, (255,255,255))  

 ###############################################################################"" 
        if lost:
            if lost_count > FPS * 3:
                run = False
          
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5            

            
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Click for play ", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()