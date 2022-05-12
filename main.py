import pygame
from pygame.locals import *

pygame.init()

#Declare window size
screen_width = 1000
screen_height = 1000

#Create and display window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')

#Game Variables
tile_size = 50


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (0, 0, 0), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (0, 0, 0), (line * tile_size, 0), (line * tile_size, screen_height))

class Player():
    def __init__(self, x , y):
        img = pygame.image.load('img/guy1.png')
        self.image = pygame.transform.scale(img, (40, 80))
        self.rect = self.image.get_rect()


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
                col_count +=1
            row_count +=1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

world_data = [
[1, 1, 1, 1, 1,],
[1, 0, 0, 0, 1,],
[1, 0, 0, 0, 1,],
[1, 0, 0, 0, 1,],
[1, 2, 2, 2, 1,],
]

world = World(world_data)

run = True
while run:

    #Draw Images to Screen
    screen.blit(bg_img, (0,0))
    screen.blit(sun_img, (100,100))
    world.draw()

    draw_grid()

    #print(world.tile_list)

    #Close window when quit is selected
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()