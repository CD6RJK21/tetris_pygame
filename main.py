import pygame
import random
import os
from shapes import *

FPS = 60
TILESIZE = 32
resolution = WIDTH, HEIGHT = 634, 800
GAME_WIDTH, GAME_HEIGHT = 320, 640
columns = 10
rows = 20

START_MOVE_TIME = 60
MOVE_TIME_INCREASE = 1.5
DIFFICULTY = 0.85


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


class Randomizer:
    def __init__(self, items_num):
        self.current_item = 0
        self.items = [i for i in range(items_num)]
        random.shuffle(self.items)

    def get_number(self):
        if self.current_item == len(self.items):
            self.current_item = 0
            self.shuffle()

        item = self.items[self.current_item]
        self.current_item += 1
        return item

    def shuffle(self):
        random.shuffle(self.items)

    def reset(self):
        self.current_item = 0
        self.shuffle()


class Grid:
    def __init__(self, columns, rows, block_dimensions, screen_res):
        self.score = 0
        self.game_over = False

        self.block_width = block_dimensions[0]
        self.block_height = block_dimensions[1]

        self.area_width = columns * self.block_width
        self.area_height = rows * self.block_height

        # top left corner of game area
        self.min_coord = ((screen_res[0] // 2 - self.area_width + 29),
                          (screen_res[1] - self.area_height) / 2 + 50)
        # bottom right corner of game area
        self.max_coord = (self.min_coord[0] + self.area_width,
                          self.min_coord[1] + self.area_height)

        # center coord of game area (letter start coord)
        self.center_coord = (self.min_coord[0] + (columns // 2) * self.block_width,
                             self.min_coord[1] + self.block_height)

        self.columns = columns
        self.rows = rows
        # rows x columns grid
        self.grid = [[-1 for i in range(self.columns)] for j in range(self.rows)]

        self.background = load_image('black_background.png')
        self.background = pygame.transform.scale(self.background, (self.area_width, self.area_height))
        self.background.set_alpha(200)

    def collided(self, letter_coords):
        indexes_list = self.convert_coords(letter_coords)
        for row_index, column_index in indexes_list:
            if row_index >= self.rows or self.grid[row_index][column_index] >= 0:
                return True
        return False

    def is_out_of_bounds(self, letter_coords):
        for x, y in letter_coords:
            if x > self.max_coord[0] - self.block_width or x < self.min_coord[0]:
                return True
        return False

    def is_game_over(self):
        return self.game_over

    def convert_coords(self, coords):
        indexes_list = []
        for coord in coords:
            column_index = int((coord[0] - self.min_coord[0]) // self.block_width)
            row_index = int((coord[1] - self.min_coord[1]) // self.block_height)
            indexes_list.append((row_index, column_index))
        return indexes_list

    def convert_indexes(self, indexes):
        coords_list = []
        for index in indexes:
            x = int(index[1] * self.block_width + self.min_coord[0])
            y = int(index[0] * self.block_height + self.min_coord[1])
            coords_list.append((x, y))
        return coords_list

    def update(self, coords, color_index):
        indexes_list = self.convert_coords(coords)
        for row_index, column_index in indexes_list:
            if row_index >= 0 and column_index >= 0:
                self.grid[row_index][column_index] = color_index

        score = 0
        # search for full rows
        for row_index, column_index in indexes_list:
            if row_index == 0:  # there is a block at the first row
                self.game_over = True

            full_row = True
            for j in range(self.columns):
                if self.grid[row_index][j] == -1:  # cell is empty
                    full_row = False
                    break

            # delete the row if it is full
            if full_row:
                del self.grid[row_index]
                score += 1
                # insert a new line at the beginning of the grid
                self.grid.insert(0, [-1 for i in range(self.columns)])
        if score == 1:
            self.score += 100
        elif score == 2:
            self.score += 300
        elif score == 3:
            self.score += 700
        elif score == 4:
            self.score += 1500
        else:
            self.score += score * 4 * 150

    def get_assist_coords(self, letter_coords):
        indexes_list = self.convert_coords(letter_coords)
        bottom = False
        collided = False

        # letter reached bottom
        for row_index, column_index in indexes_list:
            if row_index >= self.rows - 1:
                return letter_coords

        while not bottom and not collided:
            # for every block
            for i in range(len(indexes_list)):
                row_index, column_index = indexes_list[i]
                indexes_list[i] = (row_index + 1, column_index)
                # check next row
                if self.grid[row_index + 1][column_index] >= 0:
                    collided = True
                elif row_index + 1 >= self.rows - 1:
                    bottom = True

        if collided:
            i = 0
            for row_index, column_index in indexes_list:
                indexes_list[i] = (row_index - 1, column_index)
                i += 1
        return self.convert_indexes(indexes_list)

    def show(self, screen, color_blocks):
        screen.blit(self.background, self.min_coord)
        for i in range(self.rows):
            for j in range(self.columns):
                if self.grid[i][j] >= 0:  # if cell isn't empty (empty -> -1)
                    # cell value is color index
                    color_index = self.grid[i][j]
                    coord_x = self.min_coord[0] + j * self.block_width
                    coord_y = self.min_coord[1] + i * self.block_height
                    screen.blit(color_blocks[color_index], (coord_x, coord_y))

    def display_message(self, screen, font, color, message):
        text_surface = font.render(str(message), True, color).convert_alpha()
        text_x = self.min_coord[0] + (self.area_width - text_surface.get_width()) / 2
        text_y = (self.min_coord[1] + self.area_height) / 2
        screen.blit(text_surface, (text_x, text_y))

    def get_score(self):
        return self.score

    def get_center_coord(self):
        return self.center_coord


def write(font, message, color):
    text = font.render(str(message), True, color)
    text = text.convert_alpha()

    return text


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
    left_arrow = FlickeringSprite(load_image('flickering_arrow_l.png'), WIDTH // 2 - 185, HEIGHT // 2 - HEIGHT // 8 + 47)
    right_arrow = FlickeringSprite(load_image('flickering_arrow_r.png'), WIDTH // 2 + 150, HEIGHT // 2 - HEIGHT // 8 + 47)
    active_button = 'start'
    while True:
        screen.blit(background, (0, 0))
        screen.blit(logo, (5, 95))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    sound['menu_chose'].play()
                    if active_button == 'start':
                        return
                    elif active_button == 'exit':
                        exit()
                elif event.key == pygame.K_DOWN:
                    sound['menu_move'].play()
                    if active_button == 'start':
                        active_button = 'exit'
                    else:
                        active_button = 'start'
                elif event.key == pygame.K_UP:
                    sound['menu_move'].play()
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
        pygame.draw.rect(screen, (0, 0, 0), (WIDTH // 2 - 190, HEIGHT // 2 - HEIGHT // 8 + 10, 373, 150))
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


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    pygame.key.set_repeat(100, 70)

    font = pygame.font.Font(os.path.join('font', 'PressStart2P.ttf'), 34)
    background = load_image('background.png')
    game_background = load_image('game_background.png')

    randomizer = Randomizer(7)
    get_number = randomizer.get_number
    reset = randomizer.reset

    blocks = [load_image('tile1.png'), load_image('tile2.png'), load_image('tile3.png'), load_image('tile1.png'),
              load_image('tile2.png'), load_image('tile3.png'), load_image('tile1.png')]
    sound = {'menu_move': pygame.mixer.Sound('data/menu_move.ogg'),
             'menu_chose': pygame.mixer.Sound('data/menu_chose.ogg'),
             'game_end': pygame.mixer.Sound('data/game_end.ogg'),
             'new_highscore': pygame.mixer.Sound('data/new_highscore.ogg'),
             'pause': pygame.mixer.Sound('data/pause.ogg'),
             'letter_place': pygame.mixer.Sound('data/letter_place.ogg'),
             'rotate': pygame.mixer.Sound('data/rotate.ogg'),
             'letter_move': pygame.mixer.Sound('data/letter_move.ogg')
             }
    next_letter_coord = (442, 430)
    next_coord = (next_letter_coord[0] - 10, next_letter_coord[1] - 3 * TILESIZE)
    top_left = (380, 156)
    score_coord = (413, 200)
    time_coord = (18, 33)
    level_coord = (446, 615)
    highscore_coord = (416, 109)

    menu_running = True
    while menu_running:
        randomizer.reset()
        pygame.mixer.music.load('data/korobeiniki.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        main_menu(screen)

        if os.path.isfile('highscores.txt'):
            with open('highscores.txt', 'r') as file:
                highscore = file.readlines()
                highscore = [int(i.replace('\n', '')) for i in highscore]
                highscore = str(max(highscore))
        else:
            highscore = '0'

        highscore_surface = write(font, highscore, (255, 255, 255))
        highscore_played = False
        next_surface = write(font, "", (0, 0, 0))
        grid = Grid(columns, rows, (TILESIZE, TILESIZE), resolution)
        letter_move_time = 1
        current_letter = FlyingLetter((TILESIZE, TILESIZE), grid.get_center_coord(), letter_move_time, randomizer)
        next_letter = FlyingLetter((TILESIZE, TILESIZE), next_letter_coord, letter_move_time, randomizer)

        clock = pygame.time.Clock()
        total_time = 0.0
        difficulty_level = 1
        dt = 1.0 / FPS
        accumulator = 0.0
        game_running = True
        game_paused = drop_tetromino = False
        while game_running:
            screen.fill((0, 0, 0))
            screen.blit(game_background, (0, 0))
            counter = 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_running = False
                    elif event.key == pygame.K_RIGHT:
                        sound['letter_move'].play()
                        current_letter.move_right()
                        if grid.is_out_of_bounds(current_letter.get_coords()) or \
                                grid.collided(current_letter.get_coords()):
                            current_letter.move_left()
                    elif event.key == pygame.K_LEFT:
                        sound['letter_move'].play()
                        current_letter.move_left()
                        if grid.is_out_of_bounds(current_letter.get_coords()) or \
                                grid.collided(current_letter.get_coords()):
                            current_letter.move_right()
                    elif event.key == pygame.K_DOWN:
                        sound['rotate'].play()
                        current_letter.rotate_ccw()
                        # if letter collides or it is out of bounds undo rotate counterclockwise
                        if grid.is_out_of_bounds(current_letter.get_coords()) or \
                                grid.collided(current_letter.get_coords()):
                            current_letter.rotate_cw()
                    elif event.key == pygame.K_UP:
                        sound['rotate'].play()
                        current_letter.rotate_cw()
                        # if letter collides or it is out of bounds undo rotate clockwise
                        if grid.is_out_of_bounds(current_letter.get_coords()) or \
                                grid.collided(current_letter.get_coords()):
                            current_letter.rotate_ccw()
                    elif event.key == pygame.K_SPACE:
                        current_letter.speed_up()
                    elif event.key == pygame.K_p:
                        sound['pause'].play()
                        pause = True
                        while pause:
                            event = pygame.event.wait()
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                pause = False
                            elif event.type == pygame.QUIT:
                                exit()
                            grid.display_message(screen, font, (255, 255, 255), 'PAUSE')
                            pygame.display.flip()
                            pygame.display.update()
                        game_paused = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        current_letter.reset_speed()

            if game_paused:
                frame_time = dt
                game_paused = False
                clock.tick(FPS)
            else:
                frame_time = clock.tick(FPS) / 1000.0  # convert to seconds
            accumulator += frame_time
            while accumulator >= dt and game_running:
                while True:
                    current_letter.move_down(dt)
                    collided = grid.collided(current_letter.get_coords())
                    if not drop_tetromino or collided:
                        drop_tetromino = False
                        break

                if collided:
                    sound['letter_place'].play()
                    current_letter.move_up()
                    grid.update(current_letter.get_coords(), current_letter.get_color_index())
                    # increase difficulty level every time 2000 points are claimed
                    if grid.get_score() / 2000 >= difficulty_level:
                        difficulty_level += 1
                        letter_move_time *= DIFFICULTY

                    current_letter = next_letter
                    current_letter.set_coords(grid.get_center_coord())
                    current_letter.set_speed(letter_move_time)
                    next_letter = FlyingLetter((TILESIZE, TILESIZE), next_letter_coord, letter_move_time, randomizer)
                game_running = not grid.is_game_over()
                accumulator -= dt
            if grid.get_score() > int(highscore):
                if not highscore_played:
                    sound['new_highscore'].play()
                    highscore_played = True
                highscore = str(grid.get_score())
                highscore_surface = write(font, highscore, (255, 255, 255))
            total_time += frame_time
            time_string = "TIME " + '{0:02d}'.format(int(total_time // 60))\
                          + ":" + '{0:02d}'.format(int(total_time % 60))
            time_surface = write(font, time_string, (255, 255, 255))

            score_string = str(grid.get_score())
            score_surface = write(font, score_string, (255, 255, 255))
            level_string = str(difficulty_level)
            level_surface = write(font, level_string, (255, 255, 255))

            screen.blit(score_surface, score_coord)
            screen.blit(level_surface, level_coord)
            screen.blit(time_surface, time_coord)
            screen.blit(next_surface, next_coord)
            screen.blit(highscore_surface, highscore_coord)
            grid.show(screen, blocks)
            if game_running:
                current_letter.show(screen, blocks)
            next_letter.show(screen, blocks)
            pygame.display.flip()
            clock.tick(FPS)
            pygame.display.flip()

        sound['game_end'].play()
        if os.path.isfile('highscores.txt'):
            with open('highscores.txt', 'a') as file:
                file.write(str(grid.get_score()) + '\n')
        else:
            with open('highscores.txt', 'w') as file:
                file.write(str(grid.get_score()) + '\n')
        pygame.mixer.music.stop()
