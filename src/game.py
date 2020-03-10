import math

import pygame
from pygame.locals import *
from roundrects import aa_round_rect, round_rect

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
        self.grid = Grid(4)

        # TODO: Prompt user for grid size (instead of hardcoded 4x4)
        self.display_size = 640
        self.border_size = self.display_size / 80.0
        self.cell_size = ((self.display_size - self.border_size * 2) - (
                self.border_size * (self.grid.size - 1))) / self.grid.size
        self.screen = pygame.display.set_mode((self.display_size, self.display_size))
        self.screen.fill(pygame.Color("DARKGRAY"))

        # border_size + x*(border_size+cell_size)

        # TODO: Scale font size - necessary if we're gonna make nxn instead of 4x4
        pygame.font.init()
        self.font = pygame.font.Font(r"res/m5x7.ttf", 72)

        # Filter events to enqueue - we only care if the user presses an arrow key
        pygame.event.set_blocked(None)
        pygame.event.set_allowed(pygame.KEYDOWN)
        pygame.event.set_allowed(QUIT)
        pygame.event.clear()

        self.draw_grid(self.grid)
        pygame.display.flip()

    def coord(self, index):
        return self.border_size + index * (self.cell_size + self.border_size)

    def draw_grid(self, old_grid):
        # Defines cell w. spacing between cells

        # Draw each cell in the grid
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                val = self.grid.grid[y][x]
                rect = pygame.Rect(self.coord(x), self.coord(y), self.cell_size, self.cell_size)
                rounded_rect = round_rect(self.screen, rect, get_color(val), rad=10)
                # pygame.draw.rect(self.screen, get_color(val), rect)

                if val != 0:
                    text = self.font.render(str(val), False, Color("BLACK"))
                    _x = rect.centerx - text.get_rect().centerx
                    _y = rect.centery - text.get_rect().centery
                    self.screen.blit(text, (_x, _y))

        pygame.display.flip()
        self.clock.tick(60)

        # tekst starter ved 69
        # 16 starter ved 55 ca
        #
