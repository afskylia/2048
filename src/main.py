import math

import pygame
import sys
from pygame import Color
from pygame.locals import *
import pygame.freetype
from numpy.random import choice


class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.val = None

    def get_color(self):
        if self.val is None:
            return Color("GAINSBORO")

        # [2, 4, 8, 16, 32, 64, 128,256,512,1024,2048]
        index = int(math.log(self.val, 2)) - 1
        colors = [Color("IVORY"), Color("LEMONCHIFFON"), Color("SANDYBROWN"), Color("CORAL"), Color("RED"),
                  Color("YELLOW"), Color("ORANGE"), Color("LIMEGREEN"), Color("LAVENDER"), Color("LAVENDER"),
                  Color("LAVENDER")]
        return colors[index]

    def __str__(self):
        return str(self.val)
        # return str((self.x, self.y))

    def __repr__(self):
        return self.__str__()


class Grid():
    def __init__(self, size):
        self.size = size
        self.grid = [[Cell(x, y) for x in range(self.size)] for y in range(self.size)]
        self.spawn()
        self.spawn()

    def spawn(self):
        # Spawn number on random empty cell in grid
        # 75% chance for 2, 25% chance for 4
        available_cells = []
        for row in self.grid:
            for c in row:
                if c.val is None:
                    available_cells.append(c)

        cell = choice(available_cells)
        cell.val = choice([2, 4], 1, p=[0.75, 0.25])[0]

    def update(self, event):
        if event.key == K_UP:
            self.key_up()
        elif event.key == K_DOWN:
            self.key_down()
        elif event.key == K_LEFT:
            self.key_left()
        elif event.key == K_RIGHT:
            self.key_right()
        self.spawn()

        # Check event type and call the appropriate function

    def key_up(self):
        for x in range(0, self.size, 1):
            for y in range(0, self.size, 1):
                val = self.grid[x][y].val
                if val is not None:
                    while x > 0 and self.grid[x - 1][y].val is None:
                        self.grid[x][y].val = None
                        x = x - 1
                        self.grid[x][y].val = val

                    if x > 0 and self.grid[x - 1][y].val == val:
                        self.grid[x - 1][y].val = val * 2
                        self.grid[x][y].val = None

    def key_down(self):
        down_up = True
        left_right = True




        for x in range(self.size - 1, -1, -1):
            for y in range(0,self.size,1):
                print((x, y))
                val = self.grid[x][y].val
                if val is not None:
                    while x < self.size-1 and self.grid[x + 1][y].val is None:
                        self.grid[x][y].val = None
                        x = x + 1
                        self.grid[x][y].val = val

                    if x < self.size-1 and self.grid[x + 1][y].val == val:
                        self.grid[x + 1][y].val = val * 2
                        self.grid[x][y].val = None

    def key_left(self):
        print("left")
        '''
        for row in grid:
            prev = 
            for cell in row:
                if cell is not None and prev==-1: prev=cell, continue
                if cell == prev merge cell+prev
        '''

    def __str__(self):
        # return '\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.grid])
        s = [[str(e) for e in row] for row in self.grid]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        return '\n'.join(table)

    def key_right(self):
        print("right")


def run_game():
    pygame.init()

    # TODO: Prompt user for grid size (instead of hardcoded 4x4)
    display_size = 640
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((display_size, display_size))
    bg_color = Color("DARKGRAY")
    screen.fill(bg_color)

    grid = Grid(4)
    pygame.font.init()
    font = pygame.font.Font("../res/m5x7.ttf", 72)

    # TODO: Scale font size - necessary if we're gonna make nxn instead of 4x4

    def draw_grid():
        # Defines cell w. spacing between cells
        border_size = 5
        cell_size = (display_size - border_size * (grid.size - 1)) / grid.size
        cell_spacing = cell_size + border_size

        # Draw each cell in the grid
        for row in grid.grid:
            for cell in row:
                rect = pygame.Rect(cell.x * cell_spacing, cell.y * cell_spacing, cell_size, cell_size)

                pygame.draw.rect(screen, cell.get_color(), rect)

                if cell.val is not None:
                    text = font.render(str(cell.val), False, Color("BLACK"))
                    text_width, text_height = font.size(str(cell.val))
                    x = cell.x * cell_spacing + (cell_size - text_width) / 2
                    y = cell.y * cell_spacing + (cell_size - text_height) / 2
                    screen.blit(text, (x, y))

    # Filter events to enqueue - we only care if the user presses an arrow key
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(QUIT)
    pygame.event.clear()

    draw_grid()
    pygame.display.flip()
    while True:
        # TODO: Block until user does something
        event = pygame.event.wait()

        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            grid.update(event)
        else:
            continue

        draw_grid()
        print(str(grid))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_game()
