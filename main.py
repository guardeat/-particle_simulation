import pygame as pg

import random

class Block:
    EMPTY = -1,
    AIR = 0,
    SOFT = 1,
    HARD = 2,

    def __init__(self, id, color, balance_mode = EMPTY, gravity_mode = True, mass = -1):
        self.id = id
        self.color = color
        self.balance_mode = balance_mode
        self.gravity_mode = gravity_mode
        self.mass = mass

class Grid:
    def __init__(self, size_x , size_y, block_map, empty_block_id):
        self.data = [[empty_block_id for i in range(size_x)] for j in range(size_y)]
        self.block_map = block_map
        self.empty_block_id = empty_block_id

    def render(self, window: pg.Surface):
        h = window.get_height()
        w = window.get_width()
        block_width = w // len(self.data[0])
        block_height = h // len(self.data)
        for y, row in enumerate(self.data):
            for x, block_id in enumerate(row):
                block_color = self.block_map[block_id].color
                pg.draw.rect(window, block_color, (x * block_width, y * block_height, block_width, block_height))
        pg.display.flip()

    def physics(self):
        self.gravity()
        self.balance()

    def gravity(self):
        for i in range(len(self.data) - 2, -1, -1):
            for j in range(1, len(self.data[0]) - 1):
                block_up = self.block_map[self.data[i][j]]

                if block_up.balance_mode == Block.AIR:
                    continue

                block_down = self.block_map[self.data[i + 1][j]]

                if (not block_up.gravity_mode) or (not block_down.gravity_mode):
                    continue 

                if block_up.mass > block_down.mass:
                    block_up_id = self.data[i][j]
                    self.data[i][j] = self.data[i+1][j]
                    self.data[i + 1][j] = block_up_id
        
    def balance(self):
        for i in range(len(self.data) - 2, -1, -1):
            for j in range(1, len(self.data[0]) - 1):
                block = self.block_map[self.data[i][j]]

                if block.balance_mode == Block.HARD:
                    self.hard_balance(i, j)

                elif block.balance_mode == Block.SOFT:
                    self.soft_balance(i, j)

                elif block.balance_mode == Block.AIR:
                    self.air_balance(i, j)

    def hard_balance(self, i, j):
        grounded = self.check_grounded(i,j)

        has_left = self.data[i][j - 1] != self.empty_block_id
        has_right = self.data[i][j + 1] != self.empty_block_id
        has_right_below = self.data[i + 1][j - 1] != self.empty_block_id
        has_left_below = self.data[i + 1][j + 1] != self.empty_block_id

        if grounded and (not has_right) and (not has_left) and (not has_right_below) and (not has_left_below):
            if random.choice([True, False]):
                self.data[i][j - 1] = self.data[i][j]
                self.data[i][j] = self.empty_block_id
            else:
                self.data[i][j + 1] = self.data[i][j]
                self.data[i][j] = self.empty_block_id

    def soft_balance(self, i, j):
        has_right = self.data[i][j + 1] != self.empty_block_id
        has_left = self.data[i][j - 1] != self.empty_block_id

        grounded = self.check_grounded(i, j)

        if grounded:
            if random.choice([True, False]) and (not has_left):
                self.data[i][j - 1] = self.data[i][j]
                self.data[i][j] = self.empty_block_id
            elif (not has_right):
                self.data[i][j + 1] = self.data[i][j]
                self.data[i][j] = self.empty_block_id

    def air_balance(self, i, j):
        if not random.choice([True,False,False,False]):
            return

        directions = [
            (i - 1, j), 
            (i - 1, j),
            (i - 1, j),
            (i - 1, j),
            (i + 1, j),  
            (i, j - 1),  
            (i, j + 1)   
        ]

        random.shuffle(directions)
        for new_i, new_j in directions:
            if 0 <= new_i < len(self.data) and 0 <= new_j < len(self.data[0]):
                if self.data[new_i][new_j] == self.empty_block_id:
                    self.data[new_i][new_j] = self.data[i][j]
                    self.data[i][j] = self.empty_block_id
                    break

    def check_grounded(self, i ,j):
        if i == len(self.data) - 1:
            return True

        return self.data[i + 1][j] != self.empty_block_id

    def __getitem__(self, pos):
        x, y = pos
        return self.data[y][x]

    def __setitem__(self, pos, value):
        x, y = pos
        self.data[y][x] = value

def main():
    SCREEN_X = 800
    SCREEN_Y = 600
    BLOCK_SIZE = 10

    window = pg.display.set_mode((SCREEN_X, SCREEN_Y))
    pg.init()

    block_map = {
        0: Block(0, (0, 0, 0)),
        1: Block(1, (255, 0, 0),Block.HARD,True,100),
        2: Block(2, (0, 0, 255),Block.SOFT,True, 20),
        3: Block(3, (255, 255, 255),Block.AIR,True, 1),
        4: Block(4, (0, 255, 0),Block.EMPTY, False, 100000),
        5: Block(5, (255, 255, 0),Block.SOFT, True, 25)
    }

    grid = Grid(SCREEN_X // BLOCK_SIZE, SCREEN_Y // BLOCK_SIZE, block_map, 0)

    clock = pg.time.Clock()
    running = True
    mouse_pressed = False
    block_type = 1
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pressed = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_pressed = False

        if mouse_pressed:
            mouse_x, mouse_y = pg.mouse.get_pos()
            grid_x = mouse_x // BLOCK_SIZE
            grid_y = mouse_y // BLOCK_SIZE
            grid[grid_x, grid_y] = block_type

        keys = pg.key.get_pressed()
    
        if keys[pg.K_1]:
            block_type = 1
        if keys[pg.K_2]:
            block_type = 2
        if keys[pg.K_3]:
            block_type = 3
        if keys[pg.K_4]:
            block_type = 4
        if keys[pg.K_5]:
            block_type = 5

        window.fill((0, 0, 0))
        grid.physics()
        grid.render(window)

        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()