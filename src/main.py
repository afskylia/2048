import sys
from random import choice
from time import sleep

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

MOVES = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
game = None


def utility(grid, new_utility=False):
    snake_bonus, edge_bonus, merge_bonus = 0, 0, 0
    for n in range(grid.size):
        for m in range(grid.size):
            val = grid.grid[n][m]
            weight = grid.weights[n][m]
            # Bonus for following the 'snake' formation
            snake_bonus += weight * val

    if not new_utility:
        return snake_bonus
    else:
        # Bonus for having empty tiles
        empty_bonus = 1 + len(grid.free_tiles())

        monotony_bonus = 0
        for move in MOVES:
            if grid.move_is_possible(move):
                new_grid = grid.clone()
                new_grid.update(move)
                monotony_bonus += len(new_grid.free_tiles()) - len(grid.free_tiles())

        return (monotony_bonus + empty_bonus) * snake_bonus


def expectimax(grid, agent, depth, prune4=False, new_utility=False):
    if grid.game_over():
        return -1, None
    if depth == 0:
        score = utility(grid, new_utility)
        return score, None

    if agent == 'BOARD':
        score = 0

        for tile in grid.top_free_tiles(depth):
            new_grid = grid.clone()
            new_grid.spawn(2, tile)
            score += 0.9 * expectimax(new_grid, 'PLAYER', depth - 1, prune4, new_utility)[0]

            if not prune4:
                new_grid = grid.clone()
                new_grid.spawn(4, tile)
                score += 0.1 * expectimax(new_grid, 'PLAYER', depth - 1, prune4, new_utility)[0]

        return score / (len(grid.top_free_tiles(depth)) + 1), None

    elif agent == 'PLAYER':
        if len(grid.available_moves()) == 1:
            return grid.score, grid.available_moves()[0]
        score = 0
        best_move = None
        for move in grid.available_moves():
            new_grid = grid.clone()
            new_grid.update(move)
            res = expectimax(new_grid, 'BOARD', depth - 1, prune4, new_utility)[0]
            if res >= score:
                score = res
                best_move = move
        return score, best_move


def run_game(depth=5, prune4=False, dynamic_depth=False, new_utility=False):
    expectimax_enabled = True
    halfway = False

    # Filter events to enqueue - we only care if the user presses an arrow key
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(QUIT)
    pygame.event.clear()

    while True:

        # Increase depth if 1024 has been reached
        if dynamic_depth and not halfway:
            if game.grid.contains(1024):
                halfway = True
                depth += 1

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN, {})

            event.key = expectimax(game.grid, 'PLAYER', depth, prune4, new_utility)[1]
            if event.key is None:
                event.key = choice(game.grid.available_moves())
        else:
            event = pygame.event.wait()

        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in MOVES:
                if game.grid.update(event.key):  # Move successful
                    game.draw()
            else:  # Toggle expectimax
                expectimax_enabled ^= True

        if game.grid.game_over():
            return game.grid


if __name__ == "__main__":
    configs = [(5, True, False, True)]

    for config in configs:
        wins = 0
        totScore = 0
        print("Running config: " + str(config))
        for i in range(10):
            game = Game(4)  # Reset the game state and GUI
            resulting_grid = run_game(config[0], config[1], config[2], config[3])  # The resulting game state
            totScore += resulting_grid.score
            if resulting_grid.is_goal_state():
                wins += 1
            print("{} game #{} with score {}".format(
                ("Won" if resulting_grid.is_goal_state() else "Lost"), i + 1, resulting_grid.score))

        print(" ##### depth: {}, prune 4s: {}, dynamic_depth: {} #####".format(config[0], config[1], config[2]))
        print("Avg. score: {}, wins: {}".format(totScore / 10, wins))
        sleep(10)
