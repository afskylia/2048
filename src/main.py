import pygame
import sys
from random import choice

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

DIRECTIONS_DICT = {276: "LEFT", 275: "RIGHT", 273: "UP", 274: "DOWN"}  # Only for printing purposes
DIRECTIONS = [K_LEFT, K_RIGHT, K_UP, K_DOWN]


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

            score += 0.75 * expectimax(new_grid, 'PLAYER', depth - 1)[0]

            new_grid = grid.clone()
            new_grid.spawn(4, tile)
            score += 0.25 * expectimax(new_grid, 'PLAYER', depth - 1)[0]
        return [score / len(grid.empty_tiles()), None]
    else:
        score = 0
        best_dir = None
        for dir in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            new_grid = grid.clone()
            if new_grid.move_is_possible(dir):
                new_grid.update(dir)

                res = expectimax(new_grid, 'BOARD', depth - 1)
                if res[0] >= score:
                    score = res[0]
                    best_dir = dir

        return [score, best_dir]


def run_game():
    clock = pygame.time.Clock()
    game = Game()
    expectimax_enabled = False

    while True:

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN)
            event.key = expectimax(game.grid, 'PLAYER')[1]
            if event.key is None:
                event.key = choice([K_UP, K_DOWN, K_LEFT, K_RIGHT])
        else:
            event = pygame.event.wait()

        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in DIRECTIONS:
                if game.grid.update(event.key):  # Move successful
                    game.draw_grid()
                    pygame.display.flip()
                    clock.tick(60)
                else:  # Game over
                    continue  # FIXME should return score
                    # return grid.score
            else:  # Toggle expectimax
                expectimax_enabled = not expectimax_enabled  # ^=True


def main():
    while True:
        print(run_game())


if __name__ == "__main__":
    main()
