from re import S
import re
from turtle import update
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

#Declare window size
screen_width = 1000
screen_height = 1000

#Create and display window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_image = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
menu_background_img = pygame.image.load('img/menu_background.png')

#load sounds
pygame.mixer.music.load('sound/music.wav')
pygame.mixer.music.play(-1, 0.0, 2000)

coin_fx = pygame.mixer.Sound('sound/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sound/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('sound/game_over.wav')
game_over_fx.set_volume(0.5)


#Game Variables
tile_size = 50
game_over = 0
main_menu = True
level = 7
max_levels = 7
score = 0

#define colours
white = (255,255,255)
blue = (0,0,255)
black = (0,0,0)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def update_score(nscore):
    score = max_score()
    
    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

def max_score():
    with open('scores.txt' , 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()
    
    return score

#function to reset level
def reset_level(level):
    player.reset(100, screen_height -130)
    blob_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World(world_data)
    
    return world


class Button():
    def __init__(self, x , y, image):
         self.image = image
         self.rect = self.image.get_rect()
         self.rect.x = x
         self.rect.y = y
         self.clicked = False
    
    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouse over and clicked condition
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        screen.blit(self.image, self.rect)
        
        return action


class Player():
    def __init__(self, x , y):
        self.reset(x, y)

    def update(self, game_over):
        dx=0
        dy=0    
        walk_cooldown=5
        col_thresh = 20

        if game_over == 0:
            #Get key strokes
            key=pygame.key.get_pressed()
            if key[pygame.K_SPACE] or key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] or key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx-=5
                self.counter +=1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx+=5
                self.counter +=1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]   
                if self.direction == -1:
                    self.image = self.images_left[self.index]        

            #Animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]   
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            #Gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #Check Collison
            self.in_air = True
            for tile in world.tile_list:
                #x collison
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx=0
                #y collison
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #Check for collision with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()
            
            #Check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            #Check collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #Check for collision with platforms
            for platform in platform_group:
                #collision in x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #collision in y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) <col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #move with sideways with platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction


            #Update Player Posiotion
            self.rect.x +=dx
            self.rect.y +=dy

        elif game_over == -1:
            self.image = self.dead_image
            screen.blit(menu_background_img,((screen_width // 2) - 475, (screen_height // 2) - 300))
            draw_text('GAME OVER!', font, white, (screen_width // 2) - 200, screen_height // 2 - 80)

            #Draw player to screen
        screen.blit(self.image, self.rect)
            #Player collision box outline
            #pygame.draw.rect(screen, (0,0,0), self.rect, 2)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

class World():
    def __init__(self, data):
        self.tile_list =[]

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img,(tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img,(tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                
                col_count +=1
            row_count +=1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #Tile collision boxes outline
            #pygame.draw.rect(screen, (0,0,0), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter +=1
        if abs(self.move_counter) >50:
            self.move_direction *= -1
            self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter +=1
        if abs(self.move_counter) >50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
score_coin_group = pygame.sprite.Group()

#Coin for showing score
score_coin = Coin(tile_size // 2, tile_size // 2)
score_coin_group.add(score_coin)


#Load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)

restart_button = Button(screen_width // 2 - 50, screen_height // 2, restart_image)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

#Main game loop
run = True
while run:

    clock.tick(fps)
    last_score = max_score()
    key=pygame.key.get_pressed()

    #Draw Images to Screen
    screen.blit(bg_img, (0,0))
    screen.blit(sun_img, (100,100))

    if main_menu == True:
        screen.blit(menu_background_img,((screen_width // 2) - 475, (screen_height // 2) - 300))
        draw_text('High Score = ' + last_score, font, white, (screen_width // 2)- 200, screen_height // 2 -130)
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()
            #update score
            #check if coin collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('x ' + str(score), font_score, white, tile_size - 10, 10 )  

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)
        score_coin_group.draw(screen)
        game_over = player.update(game_over)

        #if player dies
        if game_over == -1:
            if restart_button.draw() or key[pygame.K_r]:
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
                
        
        #if player completes level
        if game_over == 1:
            #reset and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                screen.blit(menu_background_img,((screen_width // 2) - 475, (screen_height // 2) - 300))
                draw_text('YOU WIN!', font, white, (screen_width // 2) - 140, screen_height // 2 -180)
                draw_text('Score: ' + str(score), font, white, (screen_width // 2) - 140, screen_height // 2 -80)
                if int(score) > int(last_score):
                    draw_text('NEW HIGH SCORE!' , font, white, (screen_width // 2) - 250, screen_height // 2 -130)
                #restart game
                if restart_button.draw():
                    update_score(score)
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    #Close window when quit is selected
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()