import sys
from random import choice
from time import sleep

import pygame
import pygame.freetype
from pygame.locals import *

from game import Game

MOVES_DICT = {276: "LEFT", 275: "RIGHT", 273: "UP", 274: "DOWN"}  # Only for printing purposes
MOVES = [K_LEFT, K_RIGHT, K_UP, K_DOWN]


def neighbors_penalty(grid, pos):
    x, y = pos
    next_x, next_y = pos
    penalty = 0

    while next_x > 0:
        next_x -= 1
        if grid.grid[next_x][next_y] != 0:
            penalty += abs(grid.grid[x][y] - grid.grid[next_x][next_y])
            break
    next_x = x

    while next_x < grid.size - 1:
        next_x += 1
        if grid.grid[next_x][next_y] != 0:
            penalty += abs(grid.grid[x][y] - grid.grid[next_x][next_y])
            break
    next_x = x

    while next_y > 0:
        next_y -= 1
        if grid.grid[next_x][next_y] != 0:
            penalty += abs(grid.grid[x][y] - grid.grid[next_x][next_y])
            break
    next_y = y

    while next_y < grid.size - 1:
        next_y += 1
        if grid.grid[next_x][next_y] != 0:
            penalty += abs(grid.grid[x][y] - grid.grid[next_x][next_y])
            break

    return penalty


def utility(grid):
    W = [[32768, 16384, 8192, 4096], [256, 512, 1024, 2048], [128, 64, 32, 16], [1, 2, 4, 8]]
    score = 0
    for i in range(grid.size):
        for j in range(grid.size):
            score += W[i][j] * grid.grid[i][j]

    penalty = 0

    for y in range(grid.size):
        for x in range(grid.size):
            penalty += neighbors_penalty(grid, (x, y))

    print(score - penalty)
    return score - penalty


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

def simulate(grid, runs):
    tot = 0
    for r in range(runs):
        sim = grid.clone()
        while not (sim.game_over() or sim.is_goal_state()):
            sim.update(choice(sim.available_moves()))
        tot = tot + sim.score
    return tot/(2*runs)

def monteCarlo(grid):
    new_grid = grid.clone()
    scores = []
    for move in grid.available_moves():
        score = 0
        new_grid.update(move)
        for tile in new_grid.free_tiles():
            new_grid.spawn(2, tile)
            score = score + simulate(new_grid, 30)*0.9
            new_grid.spawn(4, tile)
            score = score + simulate(new_grid, 30)*0.1
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


def run_game():
    game = Game()
    expectimax_enabled = False

    while True:

        if expectimax_enabled and not pygame.event.peek():
            event = pygame.event.Event(KEYDOWN)
            event.key = monteCarlo(game.grid)#expectimax(game.grid, 'PLAYER')[1]
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
            else:  # Toggle expectimax
                expectimax_enabled ^= True
        if game.grid.game_over():
            return game.grid.score


if __name__ == "__main__":
    while True:
        print("Game over, your score is:", run_game())
        sleep(5)
