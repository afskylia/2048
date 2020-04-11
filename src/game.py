import pygame
from pygame.locals import *

from grid import Grid
from roundrects import aa_round_rect

COLORS = {0: Color("#D8CBBF"), 2: Color("#EEE4DA"), 4: Color("#EDE0C8"), 8: Color("#F69E91"), 16: Color("#FF6B64"),
          32: Color("#EA5751"), 64: Color("#DC3C54"), 128: Color("#F3E982"), 256: Color("#F5D35C"),
          512: Color("#F0D638"), 1024: Color("#73C6B6"), 2048: Color("#2ECC71")}

TEXT_COLORS = {0: Color("#D8CBBF"), 2: Color("#665F58"), 4: Color("#5C574E"), 8: Color("#FFF2ED"),
               16: Color("#FFF2ED"), 32: Color("#FFEFDF"), 64: Color("#FFEFDF"), 128: Color("#634C3A"),
               256: Color("#53451D"), 512: Color("#584C0D"), 1024: Color("#DFFFED"), 2048: Color("#D6FFEE")}


# Contains the game state and handles the graphics of the game
class Game:
    def __init__(self, size):

        # Initiate a game grid object
        self.grid = Grid(size)

        # Initialize the GUI
        pygame.init()
        pygame.display.set_caption("2048")
        width, height = (640, 700)  # Dimensions of the window
        self.font_small = pygame.font.Font(r"res/pixelmix.ttf", 16)
        self.font_big = pygame.font.Font(r"res/pixelmix.ttf", 36)
        self.screen = pygame.display.set_mode((width, height))
        self.background = pygame.Surface((width, height))
        self.border_size = width / 80.0
        self.cell_size = ((width - self.border_size * 2) - (self.border_size * (self.grid.size - 1))) / self.grid.size

        # Draw the background
        toolbar_border_rect = pygame.Rect(0, 0, width, height - width)
        toolbar_rect = toolbar_border_rect.inflate(-self.border_size * 2, -self.border_size * 2)
        self.game_rect = pygame.Rect(0, toolbar_border_rect.bottom, width, width)
        pygame.draw.rect(self.background, Color("#BBAD9D"), self.game_rect)
        pygame.draw.rect(self.background, Color("#93877A"), toolbar_border_rect)
        pygame.draw.rect(self.background, Color("#EFECE9"), toolbar_rect)
        self.screen.blit(self.background, (0, 0))

        # Draw instruction message
        text = self.font_small.render("Press space to toggle AI", False, TEXT_COLORS.get(4))
        text_rect = text.get_rect()
        text_rect.right = toolbar_rect.right
        self.toolbar_x = toolbar_rect.x
        self.toolbar_y = toolbar_rect.centery - text.get_rect().centery
        self.screen.blit(text, (text_rect.left - toolbar_rect.x, self.toolbar_y))

        self.draw()

    # Updates the view
    def draw(self):
        self.draw_score()
        self.draw_grid()
        pygame.display.flip()

    # Draw the current score
    def draw_score(self):
        score_text = self.font_small.render("Score: {0}".format(self.grid.score), False, TEXT_COLORS.get(4))
        surface = pygame.Surface((score_text.get_width() * 2, score_text.get_height()))
        surface.fill(Color("#EFECE9"))
        surface.blit(score_text, (0, 0))
        self.screen.blit(surface, (self.toolbar_x * 2, self.toolbar_y))

    # Draw the current game state
    def draw_grid(self):
        def coord(index):
            return self.border_size + index * (self.cell_size + self.border_size)

        for y in range(self.grid.size):
            for x in range(self.grid.size):
                val = self.grid.grid[y][x]
                rect = pygame.Rect(coord(x), coord(y)+self.game_rect.top, self.cell_size, self.cell_size)
                aa_round_rect(self.screen, rect, COLORS.get(val, Color("#4E4B65")).correct_gamma(1.3), 10,
                              self.border_size, COLORS.get(val, Color("#4E4B65")))
                if val != 0:
                    text = self.font_big.render(str(val), False, TEXT_COLORS.get(val, Color("#C3BEDF")))
                    _x = rect.centerx - text.get_rect().centerx
                    _y = rect.centery - text.get_rect().centery
                    self.screen.blit(text, (_x, _y))
