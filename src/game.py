import math

import pygame
from pygame.locals import *

from grid import Grid


def get_color(val):
    if val == 0:
        return Color("GAINSBORO")

    # [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    index = int(math.log(val, 2)) - 1
    colors = [Color("IVORY"), Color("LEMONCHIFFON"), Color("SANDYBROWN"), Color("CORAL"), Color("RED"), Color("YELLOW"),
              Color("ORANGE"), Color("LIMEGREEN"), Color("PINK"), Color("BLUE"), Color("GREEN"), Color("GREEN"), Color("GREEN"), Color("GREEN"), Color("GREEN")]
    return colors[index]


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # TODO: Prompt user for grid size (instead of hardcoded 4x4)
        self.display_size = 640
        self.screen = pygame.display.set_mode((self.display_size, self.display_size))
        self.screen.fill(pygame.Color("DARKGRAY"))
        self.grid = Grid(4)
        pygame.font.init()

        # TODO: Scale font size - necessary if we're gonna make nxn instead of 4x4
        self.font = pygame.font.Font(r"res/m5x7.ttf", 72)

        # Filter events to enqueue - we only care if the user presses an arrow key
        pygame.event.set_blocked(None)
        pygame.event.set_allowed(pygame.KEYDOWN)
        pygame.event.set_allowed(QUIT)
        pygame.event.clear()

        self.draw_grid(self.grid)
        pygame.display.flip()

    def draw_grid(self, old_grid):
        # Defines cell w. spacing between cells
        border_size = 5
        cell_size = (self.display_size - border_size * (self.grid.size - 1)) / self.grid.size
        cell_spacing = cell_size + border_size

        # Draw each cell in the grid
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                val = self.grid.grid[x][y]
                rect = pygame.Rect(y * cell_spacing, x * cell_spacing, cell_size, cell_size)
                pygame.draw.rect(self.screen, get_color(val), rect)

                if val != 0:
                    text = self.font.render(str(val), False, Color("BLACK"))
                    text_width, text_height = self.font.size(str(val))
                    _y = x * cell_spacing + (cell_size - text_height) / 2
                    _x = y * cell_spacing + (cell_size - text_width) / 2
                    self.screen.blit(text, (_x, _y))
        pygame.display.flip()
        self.clock.tick(60)
