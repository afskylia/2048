import math

import pygame
import sys
from pygame import Color
from pygame.locals import *
import pygame.freetype
from numpy.random import choice
import numpy


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

    def clear(self):
        self.val = None

    def increase(self):
        self.val = self.val * 2

    def __str__(self):
        return str(self.val)
        # return str((self.x, self.y))

    def __repr__(self):
        return self.__str__()


class Grid():
    def __init__(self, size):
        self.size = size
        # self.grid = [[Cell(x, y) for x in range(self.size)] for y in range(self.size)]
        self.grid = numpy.array([[Cell(x, y) for x in range(self.size)] for y in range(self.size)])
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
        horizontal_dir = 1
        vertical_dir = 1

        if event.key == K_UP:
            vertical_dir = 1
        elif event.key == K_DOWN:
            vertical_dir = -1
        elif event.key == K_LEFT:
            horizontal_dir = 1
        elif event.key == K_RIGHT:
            horizontal_dir = -1

        i_start = 0
        i_end = self.size - 1
        j_start = 0
        j_end = self.size - 1

        for j in range(j_start, j_end + 1, horizontal_dir):
            i = i_start

            while i < i_end:
                val = self.grid[i][j].val
                if (val is not None) and (val is self.grid[i + vertical_dir][j].val):
                    self.grid[i + vertical_dir][j].clear()
                    self.grid[i][j].increase()
                i = i + vertical_dir

            # TODO: remove whitespace after while loop
            col = self.grid[:, j]
            col = [elem for elem in col if elem.val is not None]

            x=len(col)
            while len(col) < self.size:
                col.append(Cell(x,j))
                x=x+1
            self.grid[:][j]=col

        # TODO: should only spawn if anything moved!
        self.spawn()

    def __str__(self):
        s = [[str(e) for e in row] for row in self.grid]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        return '\n'.join(table)


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
