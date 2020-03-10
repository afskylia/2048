from functools import reduce
import sys
from random import choice
from time import sleep

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

MOVES_DICT = {276: "LEFT", 275: "RIGHT", 273: "UP", 274: "DOWN"}  # Only for printing purposes
MOVES = [K_LEFT, K_RIGHT, K_UP, K_DOWN]


def grid_penalty(grid):
    def row_penalty(row):
        _penalty = 0
        for x in range(len(row)):
            next_x = x
            while next_x < len(row) - 1:
                next_x += 1
                if row[next_x] != 0:
                    _penalty += abs(row[x] - row[next_x])
                    break
        return _penalty

    def row_func(_grid): return sum([row_penalty(row) for row in _grid])
    def row_inv(_grid): return row_func([row[::-1] for row in _grid])
    def col(_grid): return row_func([list(row) for row in zip(*_grid)])
    def col_inv(_grid): return row_inv([list(row) for row in zip(*_grid)])

    return row_func(grid.grid) + row_inv(grid.grid) + col(grid.grid) + col_inv(grid.grid)


def utility(grid):
    weights = [[32768, 16384, 8192, 4096], [256, 512, 1024, 2048], [128, 64, 32, 16], [1, 2, 4, 8]]
    score = 0
    for i in range(grid.size):
        for j in range(grid.size):
            score += weights[i][j] * grid.grid[i][j]

    return score - grid_penalty(grid)


def expectimax(grid, agent, depth=0):
    # http://iamkush.me/an-artificial-intelligence-for-the-2048-game/
    # !!!!!!!!!
    if grid.game_over():
        return -1, None
    if depth >= 4:
        return utility(grid), None

    if agent == 'BOARD':
        score = 0

        if len(grid.free_tiles()) == 0:
            return 0, None

        for tile in grid.free_tiles():
            new_grid = grid.clone()
            new_grid.spawn(2, tile)

            score += 0.9 * expectimax(new_grid, 'PLAYER', depth + 1)[0]

            new_grid = grid.clone()
            new_grid.spawn(4, tile)
            score += 0.1 * expectimax(new_grid, 'PLAYER', depth + 1)[0]
        return score / len(grid.free_tiles()), None

    elif agent == 'PLAYER':
        score = 0
        best_move = None

        for move in grid.available_moves():
            new_grid = grid.clone()
            new_grid.update(move)
            res = expectimax(new_grid, 'BOARD', depth + 1)[0]
            if res >= score:  # TODO: pruning
                score = res
                best_move = move

        return score, best_move


def run_game():
    game = Game()
    expectimax_enabled = False
    expectimax_moves = 0
    start_time = None

    while True:

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN)
            event.key = expectimax(game.grid, 'PLAYER')[1]
            if event.key is None:
                event.key = choice([K_UP, K_DOWN, K_LEFT, K_RIGHT])
            expectimax_moves+=1
        else:
            event = pygame.event.wait()

        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in MOVES:
                old_grid = game.grid.clone()

                if game.grid.update(event.key):  # Move successful
                    game.draw_grid(old_grid)
            else:  # Toggle expectimax
                expectimax_enabled ^= True
                if expectimax_enabled:
                    expectimax_moves=0
                    start_time = pygame.time.get_ticks()
                else:
                    print((expectimax_moves/((pygame.time.get_ticks() - start_time) / 1000)))
        if game.grid.game_over():
            return game.grid.score


if __name__ == "__main__":
    while True:
        print("Game over, your score is:", run_game())
        sleep(5)
