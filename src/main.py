import sys
from random import choice
from time import sleep

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

MOVES = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
game = None


# Applies a function on all rows/columns of a grid and returns the sum of the results
def fold(fun, grid):
    def row_fun(_fun, _grid): return sum([_fun(row) for row in _grid])

    def row_inv(_fun, _grid): return row_fun(_fun, [row[::-1] for row in _grid])

    def col(_fun, _grid): return row_fun(_fun, [list(row) for row in zip(*_grid)])

    def col_inv(_fun, _grid): return row_inv(_fun, [list(row) for row in zip(*_grid)])

    return row_fun(fun, grid.grid) + row_inv(fun, grid.grid) + col(fun, grid.grid) + col_inv(fun, grid.grid)


# Calculates the penalty of a row based on the differences between the numbers in the row
def monotony_score(row):
    penalty = 0
    # bonus = 0  # Increases when there are more of the same number next to each other, e.g. [2,2,16,2]=4

    for x in range(len(row)):
        next_x = x
        while next_x < len(row) - 1:
            next_x += 1
            if row[next_x] != 0:
                # if row[next_x] == row[x]:
                #     bonus += row[x] ** 2
                penalty += abs(row[x] - row[next_x]) ** 2
                break
    return penalty


def utility(grid, new_utility=False):
    # TODO: i denne implementation roteres vægtmatricen tilsyneladende nogle gange:
    #  http://kstrandby.github.io/2048-Helper/
    snake_bonus, edge_bonus, merge_bonus = 0, 0, 0
    for n in range(grid.size):
        for m in range(grid.size):
            val = grid.grid[n][m]
            weight = grid.weights[n][m]
            # Bonus for following the 'snake' formation
            snake_bonus += weight * val

            # Bonus if largest numbers are on edge
            if grid.largest_number() == val and (n == 0 or n == 3 or m == 0 or m == 3):
                edge_bonus += val * weight / 2

            # Bonus for potential merges
            for neighbor in grid.neighbors((n, m)):
                if neighbor == val:
                    merge_bonus += val * weight

    if not new_utility:
        return snake_bonus
    else:
        # Bonus for having empty tiles
        empty_bonus = 1 + len(grid.free_tiles())

        # Penalize grids with low monotony
        monotony_penalty = 1 + fold(monotony_score, grid)

        # print("UTILITY: Snake bonus: {}, empty bonus: {}, edge bonus: {}, merge bonus: {}, monotony penalty: {}"
        #       .format(snake_bonus,
        #               empty_bonus,
        #               edge_bonus,
        #               merge_bonus,
        #               -monotony_penalty))
        score = ((snake_bonus + edge_bonus + merge_bonus) * edge_bonus) - monotony_penalty ** 2
        return score


def expectimax(grid, agent, depth, prune4=False, new_utility=False):
    # TODO: credit http://iamkush.me/an-artificial-intelligence-for-the-2048-game/

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

        # FIXME
        return score / (len(grid.top_free_tiles(depth)) + 1), None
        # return score, None

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


def simulate(grid, runs):
    total = 0
    for r in range(runs):
        sim = grid.clone()
        while not (sim.game_over() or sim.is_goal_state()):
            sim.update(choice(sim.available_moves()))
        total = total + sim.score
    return total / (2 * runs)


def run_game(depth=5, prune4=False, dynamic_depth=False, new_utility=False):
    expectimax_enabled = True
    halfway = False

    # Filter events to enqueue - we only care if the user presses an arrow key
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(QUIT)
    pygame.event.clear()

    while True:
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
    configs = [(4, True, True, True), (5, True, True, True), (5, False, False, True), (5, False, False, False)]
    # configs = [(4, False, False), (4, True, False), (5, True, False), (5, False, True), (5, True, True)]

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
