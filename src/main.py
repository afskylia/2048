import math
import pygame
import sys
from pygame import Color
from pygame.locals import *
import pygame.freetype
from collections import defaultdict
from random import randrange, choice


def get_color(val):
    if val == 0:
        return Color("GAINSBORO")

    # [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    index = int(math.log(val, 2)) - 1
    colors = [Color("IVORY"), Color("LEMONCHIFFON"), Color("SANDYBROWN"), Color("CORAL"), Color("RED"),
              Color("YELLOW"), Color("ORANGE"), Color("LIMEGREEN"), Color("LAVENDER"), Color("LAVENDER"),
              Color("LAVENDER")]
    return colors[index]


def transpose(grid):
    return [list(row) for row in zip(*grid)]


def invert(grid):
    return [row[::-1] for row in grid]


class Grid:
    def __init__(self, size):
        self.size = size
        self.score = 0
        # self.grid = numpy.array([[0 for x in range(self.size)] for y in range(self.size)])
        self.grid = [[0 for i in range(self.size)] for j in range(self.size)]
        self.spawn()
        self.spawn()

    def spawn(self):
        # Spawn number on random empty cell in grid
        # 75% chance for 2, 25% chance for 4
        new_val = 2 if randrange(100) <= 75 else 4
        (i, j) = choice([(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 0])
        self.grid[i][j] = new_val

    def update(self, event):
        def move_row_left(row):
            def tighten(_row):
                new_row = [i for i in _row if i != 0]
                new_row += [0 for i in range(len(_row) - len(new_row))]
                return new_row

            def merge(_row):
                pair = False
                new_row = []
                for i in range(len(_row)):
                    if pair:
                        new_row.append(2 * _row[i])
                        self.score += 2 * _row[i]
                        pair = False
                    else:
                        if i + 1 < len(_row) and _row[i] == _row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(_row[i])
                return new_row

            return tighten(merge(tighten(row)))

        moves = {K_LEFT: lambda grid: [move_row_left(row) for row in grid]}
        moves[K_RIGHT] = lambda grid: invert(moves[K_LEFT](invert(grid)))
        moves[K_UP] = lambda grid: transpose(moves[K_LEFT](transpose(grid)))
        moves[K_DOWN] = lambda grid: transpose(moves[K_RIGHT](transpose(grid)))

        if event.key in moves:
            if self.move_is_possible(event.key):
                self.grid = moves[event.key](self.grid)
                self.spawn()
                return True
            else:
                return False

    def move_is_possible(self, dir):
        def row_is_left_movable(row):
            def change(i):  # true if there'll be change in i-th tile
                if row[i] == 0 and row[i + 1] != 0:  # Move
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:  # Merge
                    return True
                return False

            return any(change(i) for i in range(len(row) - 1))

        check = {K_LEFT: lambda field: any(row_is_left_movable(row) for row in field)}
        check[K_RIGHT] = lambda field: check[K_LEFT](invert(field))
        check[K_UP] = lambda field: check[K_LEFT](transpose(field))
        check[K_DOWN] = lambda field: check[K_RIGHT](transpose(field))

        if dir in check:
            return check[dir](self.grid)
        else:
            return False

    def victory(self):
        return any(any(i >= 2048 for i in row) for row in self.grid)

    def gameover(self):
        return not any(self.move_is_possible(move) for move in [K_UP, K_DOWN, K_RIGHT, K_LEFT])

    def __getitem__(self, pos):
        x, y = pos
        return self.grid[x][y]

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
                rect = pygame.Rect(x * cell_spacing, y * cell_spacing, cell_size, cell_size)
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
    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if grid.update(event):  # move successful
                draw_grid()
                pygame.display.flip()

                if grid.victory():
                    return grid.score, True
                elif grid.gameover():
                    return grid.score, False
                else:
                    clock.tick(60)
        else:  # unexpected event type
            continue


def main():
    while True:
        score, victory = run_game()
        if victory:
            print("You won! Score:", score)
        else:
            print("Game over! Score:", score)


if __name__ == "__main__":
    main()
