from copy import deepcopy
from random import randrange, choice

from pygame.locals import *


def transpose(grid):
    return [list(row) for row in zip(*grid)]


def invert(grid):
    return [row[::-1] for row in grid]


# Object containing the game state (grid) and different functions for manipulating the grid
class Grid:
    def __init__(self, size, score=0, grid=None):
        self.size = size
        self.score = score

        # Generate weight matrix
        weights = [2 ** n for n in range(0, self.size * self.size)][::-1]
        weights = [weights[i:i + self.size] for i in range(0, self.size * self.size, self.size)]
        self.weights = [weights[i] if i % 2 == 0 else (weights[i])[::-1] for i in range(self.size)]

        # Generate order matrix
        self.order = []
        x, y, i, j = 0, 0, 0, 1
        while not (len(self.order) == self.size * self.size):
            self.order.append((x, y))
            if i == self.size - 1:
                y = self.size - 1 if j == 1 else 0
                j *= -1
                x += 1
                i = 0
            else:
                y += j
                i += 1

        # Spawn initial cells if new game
        if grid is None:
            self.grid = [[0 for i in range(size)] for j in range(size)]
            self.spawn()
            self.spawn()
        else:
            self.grid = grid

    def clone(self):
        return Grid(self.size, self.score, deepcopy(self.grid))

    def neighbors(self, pos):
        x, y = pos
        neighbors = []
        for neighbor in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            _x, _y = neighbor
            try:
                neighbors.append(self.grid[_x][_y])
            except IndexError:
                continue

        return neighbors

    def free_tiles(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 0]

    def top_free_tiles(self, num):
        tiles = []
        remaining = num
        for tile in self.order:
            if remaining > 0:
                if self.grid[tile[0]][tile[1]] == 0:
                    tiles.append(tile)
                    remaining = remaining - 1
            else:
                return tiles
        return tiles

    def spawn(self, val=None, pos=None):
        # Spawn number on a cell in the grid
        val = val if val is not None else 2 if randrange(100) <= 90 else 4
        i, j = pos if pos is not None else choice(self.free_tiles())
        self.grid[i][j] = val

    def update(self, move):
        # Updates the grid in the specified direction

        # Inspiration for implementation of the merge_left(row) function has been taken from:
        # https://github.com/Fennay/python-study/blob/master/2048/2048.py
        def merge_left(row):
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

            def remove_empty_tiles(_row):
                new_row = [i for i in _row if i != 0]
                new_row += [0 for i in range(len(_row) - len(new_row))]
                return new_row

            return remove_empty_tiles(merge(remove_empty_tiles(row)))

        moves = {K_LEFT: lambda grid: [merge_left(row) for row in grid]}
        moves[K_RIGHT] = lambda grid: invert(moves[K_LEFT](invert(grid)))
        moves[K_UP] = lambda grid: transpose(moves[K_LEFT](transpose(grid)))
        moves[K_DOWN] = lambda grid: transpose(moves[K_RIGHT](transpose(grid)))

        if move in moves and self.move_is_possible(move):
            self.grid = moves[move](self.grid)
            self.spawn()
            return True
        else:
            return False

    def move_is_possible(self, move):
        def row_is_left_movable(row):
            def change(i):
                if row[i] != 0 and row[i + 1] == row[i]:  # Merge
                    return True
                if row[i] == 0 and row[i + 1] != 0:  # Move
                    return True
                return False

            return any(change(i) for i in range(len(row) - 1))

        check = {K_LEFT: lambda field: any(row_is_left_movable(row) for row in field)}
        check[K_RIGHT] = lambda field: check[K_LEFT](invert(field))
        check[K_UP] = lambda field: check[K_LEFT](transpose(field))
        check[K_DOWN] = lambda field: check[K_RIGHT](transpose(field))

        return False if move not in check else check[move](self.grid)

    def available_moves(self):
        moves = []
        for move in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            if self.move_is_possible(move):
                moves.append(move)
        return moves

    def largest_number(self):
        return max(map(max, self.grid))

    def contains(self, val):
        return any(val in row for row in self.grid)

    def is_goal_state(self):
        return any(any(i >= 2048 for i in row) for row in self.grid)

    def game_over(self):
        return len(self.available_moves()) == 0

    def __str__(self):
        s = [[str(e) for e in row] for row in self.grid]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        return '\n'.join(table)
