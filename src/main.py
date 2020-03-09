import math
import pygame
import sys
from pygame import Color
from pygame.locals import *
import pygame.freetype
from collections import defaultdict
from random import randrange, choice
from copy import copy, deepcopy
from grid import Grid

DIRECTIONS_DICT = {276: "LEFT", 275: "RIGHT", 273: "UP", 274: "DOWN"}
DIRECTIONS = [K_LEFT, K_RIGHT, K_UP, K_DOWN]


def get_color(val):
    if val == 0:
        return Color("GAINSBORO")

    # [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    index = int(math.log(val, 2)) - 1
    colors = [Color("IVORY"), Color("LEMONCHIFFON"), Color("SANDYBROWN"), Color("CORAL"), Color("RED"),
              Color("YELLOW"), Color("ORANGE"), Color(
                  "LIMEGREEN"), Color("LAVENDER"), Color("LAVENDER"),
              Color("LAVENDER")]
    return colors[index]


def expectimax(grid, agent, depth=4):
    if grid.gameover():
        return [-1, None]
    if depth == 0 or grid.victory():
        return [grid.score, None]

    if agent == 'BOARD':
        score = 0

        if len(grid.empty_tiles()) == 0:
            return [0, None]

        for tile in grid.empty_tiles():
            new_grid = grid.clone()
            new_grid.spawn(2, tile)

            score += 0.75*expectimax(new_grid, 'PLAYER', depth-1)[0]

            new_grid = grid.clone()
            new_grid.spawn(4, tile)
            score += 0.25*expectimax(new_grid, 'PLAYER', depth-1)[0]
        return [score/len(grid.empty_tiles()), None]
    else:
        score = 0
        best_dir = None
        for dir in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            new_grid = grid.clone()
            if new_grid.move_is_possible(dir):
                new_grid.update(dir)

                res = expectimax(new_grid, 'BOARD', depth-1)
                if res[0] >= score:
                    score = res[0]
                    best_dir = dir

        return [score, best_dir]


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
    font = pygame.font.Font(r"res/m5x7.ttf", 72)

    # TODO: Scale font size - necessary if we're gonna make nxn instead of 4x4

    def draw_grid():
        # Defines cell w. spacing between cells
        border_size = 5
        cell_size = (display_size - border_size * (grid.size - 1)) / grid.size
        cell_spacing = cell_size + border_size

        # Draw each cell in the grid
        for y in range(grid.size):
            row = grid.grid[y]

            for x in range(grid.size):
                val = row[x]
                rect = pygame.Rect(x * cell_spacing, y *
                                   cell_spacing, cell_size, cell_size)
                pygame.draw.rect(screen, get_color(val), rect)

                if val != 0:
                    text = font.render(str(val), False, Color("BLACK"))
                    text_width, text_height = font.size(str(val))
                    _y = y * cell_spacing + (cell_size - text_height) / 2
                    _x = x * cell_spacing + (cell_size - text_width) / 2
                    screen.blit(text, (_x, _y))

    # Filter events to enqueue - we only care if the user presses an arrow key
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(QUIT)
    pygame.event.clear()

    draw_grid()
    pygame.display.flip()
    expectimax_enabled = False

    while True:

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN)
            event.key = expectimax(grid, 'PLAYER')[1]
            if event.key is None:
                event.key = choice([K_UP, K_DOWN, K_LEFT, K_RIGHT])
        else:
            event = pygame.event.wait()
            
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in DIRECTIONS:
                if grid.update(event.key):  # Move successful
                    draw_grid()
                    pygame.display.flip()
                    clock.tick(60)
                else:   # Game over
                    return grid.score
            else:   # Toggle expectimax
                expectimax_enabled = not expectimax_enabled  # ^=True


def main():
    while True:
        print(run_game())


if __name__ == "__main__":
    main()
