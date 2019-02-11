import pygame
import random
import os
from shapes import *

FPS = 60
TILESIZE = 64
resolution = WIDTH, HEIGHT = 1024, 896
GAME_WIDTH, GAME_HEIGHT = 320, 640

START_MOVE_TIME = 60
MOVE_TIME_INCREASE = 1.5


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def create_grid(pre_init_pos={}):
    grid = [[0 for _ in range(10)] for _ in range(20)]
    for i in range(20):
        for j in range(10):
            if (i, j) not in pre_init_pos:
                grid[i][j] = pygame.sprite.Sprite(static_tiles)
                grid[i][j].image = load_image('black_tile.png')
                grid[i][j].rect = grid[i][j].image.get_rect()
                grid[i][j].rect.x = top_left[0] + j * (TILESIZE // 2)
                grid[i][j].rect.y = top_left[1] + i * (TILESIZE // 2)
    return grid


def get_random_shape():
    return random.choice(shapes)


def draw_grid(surface):
    surface.blit(game_background, (0, 0))
    #  pygame.draw.rect(surface, (0, 191, 255), (top_left[0] - 10, top_left[1] - 10, GAME_WIDTH + 20, GAME_HEIGHT + 20))
    static_tiles.draw(surface)


class FlickeringSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, flickering_timeout=20):
        self.sprite_group = pygame.sprite.Group()
        super().__init__(self.sprite_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.flickering_timeout = flickering_timeout
        self.time_to_timeout = 0
        self.time = 0
        self.timeout_time = 0
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        if self.timeout_time > 0:
            self.sprite_group.draw(screen)
            self.timeout_time -= 1
        else:
            if self.time == 0:
                self.sprite_group.draw(screen)

    def update(self):
        self.time += (self.time + 1) % 2
        self.time_to_timeout += 1

        if self.time_to_timeout >= self.flickering_timeout:
            self.timeout_time = 10
            self.time_to_timeout = 0


class FlyingLetter:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.image = tile_images
        self.rotation = 0


def main_menu(screen):
    clock = pygame.time.Clock()
    background = load_image('background.png')
    logo = load_image('logo.png')
    text = ['START GAME', 'EXIT']
    text_coord_y = HEIGHT // 2 - HEIGHT // 8
    text_coord_x = WIDTH // 2
    font = pygame.font.Font('font/PressStart2P.ttf', 30)
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord_y += intro_rect.height + 20
        text_height = intro_rect.height + 20
        intro_rect.top = text_coord_y
        intro_rect.x = text_coord_x - intro_rect.width // 2
        screen.blit(string_rendered, intro_rect)
    # TODO: made black background for text in main menu
    left_arrow = FlickeringSprite(load_image('flickering_arrow_l.png'), WIDTH // 2 - 185, HEIGHT // 2 - HEIGHT // 8 + 47)
    right_arrow = FlickeringSprite(load_image('flickering_arrow_r.png'), WIDTH // 2 + 150, HEIGHT // 2 - HEIGHT // 8 + 47)
    active_button = 'start'
    while True:
        screen.blit(background, (0, 0))
        screen.blit(logo, (170, 95))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active_button == 'start':
                        return
                    elif active_button == 'exit':
                        exit()
                elif event.key == pygame.K_DOWN:
                    if active_button == 'start':
                        active_button = 'exit'
                    else:
                        active_button = 'start'
                elif event.key == pygame.K_UP:
                    if active_button == 'start':
                        active_button = 'exit'
                    else:
                        active_button = 'start'

        if active_button == 'start':
            left_arrow.rect.x, left_arrow.rect.y = WIDTH // 2 - 185, HEIGHT // 2 - HEIGHT // 8 + 47
            right_arrow.rect.x, right_arrow.rect.y = WIDTH // 2 + 150, HEIGHT // 2 - HEIGHT // 8 + 47
        elif active_button == 'exit':
            left_arrow.rect.x, left_arrow.rect.y = WIDTH // 2 - 95, HEIGHT // 2 - HEIGHT // 8 + 100
            right_arrow.rect.x, right_arrow.rect.y = WIDTH // 2 + 55, HEIGHT // 2 - HEIGHT // 8 + 100
        text_coord_y = HEIGHT // 2 - HEIGHT // 8
        for line in text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord_y += intro_rect.height + 20
            intro_rect.top = text_coord_y
            intro_rect.x = text_coord_x - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        left_arrow.update()
        right_arrow.update()
        left_arrow.draw(screen)
        right_arrow.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

main_menu(screen)
background_image = load_image('background.png')
game_background = load_image('game_background.png')

tile_images = [load_image('tile1.png'), load_image('tile3.png'), load_image('tile2.png'),
                   load_image('tile1.png'), load_image('tile3.png'), load_image('tile2.png')]
# top_left = ((WIDTH - GAME_WIDTH) // 2, HEIGHT - GAME_HEIGHT - 10)
top_left = (380, 156)

static_tiles = pygame.sprite.Group()
grid = create_grid()

running = True
while running:
    screen.fill((0, 0, 0))
    draw_grid(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                pass
    clock.tick(FPS)
    pygame.display.flip()