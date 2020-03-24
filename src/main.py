from functools import reduce
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

    grid = grid.grid
    return row_fun(fun, grid) + row_inv(fun, grid) + col(fun, grid) + col_inv(fun, grid)


# Calculates the penalty of a row based on the differences between the numbers in the row
def row_score(row):
    penalty = 0
    monotony_score = 0  # Increases when there are more of the same number next to each other, e.g. [2,2,16,2]=4

    for x in range(len(row)):
        next_x = x
        while next_x < len(row) - 1:
            next_x += 1
            if row[next_x] != 0:
                if row[next_x] == row[x]:
                    monotony_score += row[x] * 2
                penalty += abs(row[x] - row[next_x])
                break
    return penalty - monotony_score


def utility(grid):
    # TODO: i denne implementation roteres vægtmatricen tilsyneladende nogle gange
    # http://kstrandby.github.io/2048-Helper/
    score = 0

    edge_weights = [[16, 16, 16, 16],
                    [8, 1, 1, 8],
                    [4, 1, 1, 4],
                    [2, 2, 2, 2]]

    # Rewards grids for following the 'snake' formation and for being on the edge
    for i in range(grid.size):
        for j in range(grid.size):
            score += game.weights[i][j] * grid.grid[i][j]  #* edge_weights[i][j]

    # Penalize grids with low monotony
    grid_penalty = fold(row_score, grid)
    # Rewards grids with many free tiles
    score += len(grid.free_tiles()) ** grid.size

    score /= grid.size  # TODO: Not sure if this does anything
    return score - grid_penalty


def expectimax(grid, agent, depth, prune4=False):
    # http://iamkush.me/an-artificial-intelligence-for-the-2048-game/
    # !!!!!!!!!
    if grid.game_over():
        return -1, None
    if depth == 0: #or len(grid.available_moves()) == 1 ???
        return utility(grid), None

    if agent == 'BOARD':
        score = 0

        if len(grid.free_tiles()) == 0:
            return -100000, None

        for tile in grid.top_free_tiles(depth):
            new_grid = grid.clone()
            new_grid.spawn(2, tile)
            score += 0.9 * expectimax(new_grid, 'PLAYER', depth - 1)[0]
            if not prune4:
                new_grid = grid.clone()
                new_grid.spawn(4, tile)
                score += 0.1 * expectimax(new_grid, 'PLAYER', depth - 1)[0]
        return score / len(grid.top_free_tiles(depth)), None

    elif agent == 'PLAYER':
        if len(grid.available_moves()) == 1:
            return grid.score, grid.available_moves()[0]

        score = 0
        best_move = None

        for move in grid.available_moves():
            new_grid = grid.clone()
            new_grid.update(move)
            res = expectimax(new_grid, 'BOARD', depth - 1)[0]
            if res >= score:  # TODO: pruning
                score = res
                best_move = move

        return score, best_move


def simulate(grid, runs):
    tot = 0
    for r in range(runs):
        sim = grid.clone()
        while not (sim.game_over() or sim.is_goal_state()):
            sim.update(choice(sim.available_moves()))
        tot = tot + sim.score
    return tot / (2 * runs)


def monteCarlo(grid):
    new_grid = grid.clone()
    scores = []
    for move in grid.available_moves():
        score = 0
        new_grid.update(move)
        for tile in new_grid.free_tiles():
            new_grid.spawn(2, tile)
            score = score + simulate(new_grid, 30) * 0.9
            new_grid.spawn(4, tile)
            score = score + simulate(new_grid, 30) * 0.1
        scores.append((move, score))
    if not grid.game_over():
        bestM = scores[0][0]
        bestS = scores[0][1]
        for i in range(len(scores)):
            if scores[i][1] > bestS:
                bestS = scores[i][1]
                bestM = scores[i][0]
        return bestM
    return None


def run_game(depth=5, prune4 = False):
    game = Game()
    expectimax_enabled = True
    expectimax_moves = 0
    #start_time = None

    while True:

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN)
            #size = len(game.grid.free_tiles())
            # depth = 4 if size >= 8 else 8 if size <= 2 else 5
            event.key = expectimax(game.grid, 'PLAYER', depth, prune4)[1]

            if event.key is None:
                event.key = choice(game.grid.available_moves())
            expectimax_moves += 1
        else:
            event = pygame.event.wait()

        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in MOVES:
                old_grid = game.grid.clone()

                if game.grid.update(event.key):  # Move successful
                    game.draw_grid()
            else:  # Toggle expectimax
                expectimax_enabled ^= True
                """
                if expectimax_enabled:
                    expectimax_moves = 0
                    start_time = pygame.time.get_ticks()
                else:
                    print((expectimax_moves/((pygame.time.get_ticks() - start_time) / 1000)))
                    """
        if game.grid.game_over():
            return game


if __name__ == "__main__":
    configs = [(4, False), (4, True), (5, False), (5, True)]
    for config in configs:
        wins = 0
        totScore = 0
        for i in range(10):
            game = run_game(config[0], config[1])
            print(game.score)
            print(game.is_goal_state(), "\n")
            totScore += game.score
            if game.is_goal_state():
                wins += 1
        print(" --- depth: ", config[0], ", prune 4s: ", config[1], " ---")
        print("Avg. score: ", totScore/10, ", wins: ", wins)
    sleep(10)
