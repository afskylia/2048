import pygame
from pygame.locals import *

from grid import Grid
from roundrects import aa_round_rect

COLORS = {0: Color("#D8CBBF"), 2: Color("#EEE4DA"), 4: Color("#EDE0C8"), 8: Color("#F69E91"), 16: Color("#FF6B64"),
          32: Color("#EA5751"), 64: Color("#DC3C54"), 128: Color("#F3E982"), 256: Color("#F5D35C"),
          512: Color("#F0D638"), 1024: Color("#73C6B6"), 2048: Color("#2ECC71")}

TEXT_COLORS = {0: Color("#D8CBBF"), 2: Color("#665F58"), 4: Color("#5C574E"), 8: Color("#FFF2ED"),
               16: Color("#FFF2ED"), 32: Color("#FFEFDF"), 64: Color("#FFDFCE"), 128: Color("#634C3A"),
               256: Color("#53451D"), 512: Color("#584C0D"), 1024: Color("#DFFFED"), 2048: Color("#D6FFEE")}


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.grid = Grid(4)

        # TODO: Prompt user for grid size (instead of hardcoded 4x4)
        self.display_size = 640
        self.border_size = self.display_size / 80.0
        self.cell_size = ((self.display_size - self.border_size * 2) - (
                    self.border_size * (self.grid.size - 1))) / self.grid.size
        self.screen = pygame.display.set_mode((self.display_size, self.display_size))
        self.screen.fill(pygame.Color("#BBAD9D"))
        # TODO: Show a box that says how to enable the AI, score etc

        # TODO: Scale font size - necessary if we're gonna make nxn instead of 4x4
        pygame.font.init()
        self.font = pygame.font.Font(r"res/pixelmix.ttf", 36)

        # Filter events to enqueue - we only care if the user presses an arrow key
        pygame.event.set_blocked(None)
        pygame.event.set_allowed(pygame.KEYDOWN)
        pygame.event.set_allowed(QUIT)
        pygame.event.clear()

        self.draw_grid()
        pygame.display.flip()

    def coord(self, index):
        return self.border_size + index * (self.cell_size + self.border_size)

    def draw_grid(self):
        # Draw each cell in the grid
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                val = self.grid.grid[y][x]
                rect = pygame.Rect(self.coord(x), self.coord(y), self.cell_size, self.cell_size)
                aa_round_rect(self.screen, rect, COLORS.get(val, Color("#4E4B65")).correct_gamma(1.3), 10,
                              self.border_size, COLORS.get(val, Color("#4E4B65")))
                if val != 0:
                    text = self.font.render(str(val), False, TEXT_COLORS.get(val, Color("#C3BEDF")))
                    _x = rect.centerx - text.get_rect().centerx
                    _y = rect.centery - text.get_rect().centery
                    self.screen.blit(text, (_x, _y))

        pygame.display.flip()
        self.clock.tick(60)
