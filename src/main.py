import sys
from random import choice

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

MOVES_DICT = {276: "LEFT", 275: "RIGHT", 273: "UP", 274: "DOWN"}  # Only for printing purposes
MOVES = [K_LEFT, K_RIGHT, K_UP, K_DOWN]


def utility(grid):
    W = [[6, 5, 4, 3], [5, 4, 3, 2], [4, 3, 2, 1], [3, 2, 1, 0]]
    score = 0
    for i in range(grid.size):
        for j in range(grid.size):
            score += W[i][j] * grid.grid[i][j]

    penalty = 0

    for y in range(grid.size):
        for x in range(grid.size):
            neighbors = []  # FIXME: Neighbors tager lige nu ikke højde for tomme pladser!! Skal bruge tighten først
            if x>0:
                neighbors.append((x - 1, y))
            if x < grid.size - 1:
                neighbors.append((x + 1, y))
            if y > 0:
                neighbors.append((x, y - 1))
            if y < grid.size - 1:
                neighbors.append((x, y + 1))

            for neighbor in neighbors:
                _x, _y = neighbor
                penalty += abs(grid.grid[x][y] - grid.grid[_x][_y])

    print(score - penalty)
    return score - penalty


def expectimax(grid, agent, depth=0):
    # http://iamkush.me/an-artificial-intelligence-for-the-2048-game/
    # !!!!!!!!!
    if grid.game_over():
        return -1, None
    if depth >= 4 or grid.is_goal_state():
        return utility(grid), None

    if agent == 'BOARD':
        score = 0

        if len(grid.free_tiles()) == 0:
            return 0, None

        for tile in grid.free_tiles():
            new_grid = grid.clone()
            new_grid.spawn(2, tile)

            score += 0.75 * expectimax(new_grid, 'PLAYER', depth + 1)[0]

            new_grid = grid.clone()
            new_grid.spawn(4, tile)
            score += 0.25 * expectimax(new_grid, 'PLAYER', depth + 1)[0]
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
            if event.key in MOVES:
                old_grid = game.grid.clone()

                if game.grid.update(event.key):  # Move successful
                    game.draw_grid(old_grid)
                else:  # Game over
                    continue  # FIXME should return score
                    # return grid.score
            else:  # Toggle expectimax
                expectimax_enabled = not expectimax_enabled  # ^=True


if __name__ == "__main__":
    while True:
        print(run_game())
