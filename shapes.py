class FlyingLetter:
    i_letter_angle_0 = ["....",
                           "####",
                           "....",
                           "...."]

    # rotate 90 degrees cw (clockwise)
    i_letter_angle_90 = [".#..",
                            ".#..",
                            ".#..",
                            ".#.."]

    i_letter = (i_letter_angle_0, i_letter_angle_90,
                   i_letter_angle_0, i_letter_angle_90)

    # O letter
    o_letter_angle_0 = ["##..",
                           "##..",
                           "....",
                           "...."]

    o_letter = (o_letter_angle_0, o_letter_angle_0,
                   o_letter_angle_0, o_letter_angle_0)

    # T letter
    t_letter_angle_0 = [".#..",
                           "###.",
                           "....",
                           "...."]

    # rotate 90 degrees cw
    t_letter_angle_90 = [".#..",
                            ".##.",
                            ".#..",
                            "...."]

    # rotate 180 degrees cw
    t_letter_angle_180 = ["....",
                             "###.",
                             ".#..",
                             "...."]

    # rotate 270 degrees cw
    t_letter_angle_270 = [".#..",
                             "##..",
                             ".#..",
                             "...."]

    t_letter = (t_letter_angle_0, t_letter_angle_90,
                   t_letter_angle_180, t_letter_angle_270)

    # J letter
    j_letter_angle_0 = ["#...",
                           "###.",
                           "....",
                           "...."]

    # rotate 90 degrees cw
    j_letter_angle_90 = [".##.",
                            ".#..",
                            ".#..",
                            "...."]

    # rotate 180 degrees cw
    j_letter_angle_180 = ["....",
                             "###.",
                             "..#.",
                             "...."]

    # rotate 270 degrees cw
    j_letter_angle_270 = [".#..",
                             ".#..",
                             "##..",
                             "...."]

    j_letter = (j_letter_angle_0, j_letter_angle_90,
                   j_letter_angle_180, j_letter_angle_270)

    # L letter cw
    l_letter_angle_0 = ["..#.",
                           "###.",
                           "....",
                           "...."]

    # rotate 90 degrees cw
    l_letter_angle_90 = [".#..",
                            ".#..",
                            ".##.",
                            "...."]

    # rotate 180 degrees cw
    l_letter_angle_180 = ["....",
                             "###.",
                             "#...",
                             "...."]

    # rotate 270 degrees cw
    l_letter_angle_270 = ["##..",
                             ".#..",
                             ".#..",
                             "...."]

    l_letter = (l_letter_angle_0, l_letter_angle_90,
                   l_letter_angle_180, l_letter_angle_270)

    # S letter
    s_letter_angle_0 = [".##.",
                           "##..",
                           "....",
                           "...."]

    # rotate 90 degrees cw
    s_letter_angle_90 = [".#..",
                            ".##.",
                            "..#.",
                            "...."]

    s_letter = (s_letter_angle_0, s_letter_angle_90,
                   s_letter_angle_0, s_letter_angle_90)

    # Z letter
    z_letter_angle_0 = ["##..",
                           ".##.",
                           "....",
                           "...."]

    # rotate 90 degrees cw
    z_letter_angle_90 = ["..#.",
                            ".##.",
                            ".#..",
                            "...."]

    z_letter = (z_letter_angle_0, z_letter_angle_90,
                   z_letter_angle_0, z_letter_angle_90)

    letters = (i_letter, o_letter, t_letter, j_letter,
                   l_letter, s_letter, z_letter)

    fast_move_time = 0.03  # seconds

    def __init__(self, block_dimensions, coord, move_time, randomizer):
        self.random_index = randomizer.get_number()
        self.random_letter = FlyingLetter.letters[self.random_index]

        self.current_angle = 0
        self.current_frame = self.random_letter[self.current_angle]

        self.block_width = block_dimensions[0]
        self.block_height = block_dimensions[1]

        # coordinates of the center block (required for the rotation)
        self.center_coord = list(coord)

        # coordinates for each block of the letter
        # list of coordinates [x, y]
        self.blocks_coords = self.build()

        # time in seconds
        self.normal_move_time = move_time
        self.move_time = self.normal_move_time
        self.elapsed_time = 0.0

    def build(self):
        x, y = [self.center_coord[0] - self.block_width, self.center_coord[1]
                - self.block_height]
        letter_coords = []

        for i in range(len(self.current_frame)):
            for char in self.current_frame[i]:
                if char == '#':
                    letter_coords.append([x, y])
                x += self.block_width
            x = self.center_coord[0] - self.block_width
            y += self.block_height
        return letter_coords

    def set_coords(self, center_coord):
        self.center_coord = list(center_coord)
        self.blocks_coords = self.build()

    def get_coords(self):
        return self.blocks_coords

    def get_color_index(self):
        return self.random_index

    def speed_up(self):
        self.move_time = FlyingLetter.fast_move_time

    def reset_speed(self):
        self.move_time = self.normal_move_time

    def set_speed(self, move_time):
        self.normal_move_time = move_time
        self.move_time = self.normal_move_time

    def show(self, screen, color_blocks):
        for coord in self.blocks_coords:
            screen.blit(color_blocks[self.random_index], coord)

    def move_up(self):
        for coord in self.blocks_coords:
            coord[1] -= self.block_height
        self.center_coord[1] -= self.block_height

    def move_down(self, time):
        self.elapsed_time += time
        if self.elapsed_time >= self.move_time:
            self.elapsed_time = 0
            for coord in self.blocks_coords:
                coord[1] += self.block_height
            self.center_coord[1] += self.block_height

    def move_left(self):
        self.center_coord[0] -= self.block_width
        for coord in self.blocks_coords:
            coord[0] -= self.block_width

    def move_right(self):
        self.center_coord[0] += self.block_width
        for coord in self.blocks_coords:
            coord[0] += self.block_width

    def rotate_ccw(self):
        if self.current_angle == 0:
            self.current_angle = 3
        else:
            self.current_angle -= 1

        self.current_frame = self.random_letter[self.current_angle]
        self.blocks_coords = self.build()

    def rotate_cw(self):
        self.current_angle = (self.current_angle + 1) % 4
        self.current_frame = self.random_letter[self.current_angle]
        self.blocks_coords = self.build()
