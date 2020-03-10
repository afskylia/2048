import math

import pygame
from pygame.locals import *
from roundrects import aa_round_rect, round_rect

from grid import Grid

COLORS = {0: Color("#D8CBBF"), 2: Color("#EEE4DA"), 4: Color("#EDE0C8"), 8: Color("#EDBB99"), 16: Color("#ED7C61"),
          32: Color("#EC6757"), 64: Color("#EC3E44"), 128: Color("#F9E79F"), 256: Color("#F7D465"),
          512: Color("#F0DA0B"), 1024: Color("#73C6B6"), 2048: Color("#2ECC71")}

TEXT_COLORS = {0: Color("#D8CBBF"), 2: Color("#665F58"), 4: Color("#5C574E"), 8: Color("#693D2F"),
               16: Color("#FFF2ED"), 32: Color("#FFEFDF"), 64: Color("#FFDFCE"), 128: Color("#644D2F"),
               256: Color("#5A4728"), 512: Color("#675820"), 1024: Color("#DFFFED"), 2048: Color("#D4F3E1")}


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
        self.screen.fill(pygame.Color("#BBAD9D"))

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
                rounded_rect = round_rect(self.screen, rect, COLORS.get(val,Color("#4E4B65")), rad=8)
                # pygame.draw.rect(self.screen, get_color(val), rect)

                if val != 0:
                    text = self.font.render(str(val), False, TEXT_COLORS.get(val,Color("#C3BEDF")))
                    _x = rect.centerx - text.get_rect().centerx
                    _y = rect.centery - text.get_rect().centery
                    self.screen.blit(text, (_x, _y))

        pygame.display.flip()
        self.clock.tick(60)

        # tekst starter ved 69
        # 16 starter ved 55 ca
        #
