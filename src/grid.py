from copy import deepcopy
from random import randrange, choice

from pygame.locals import *


def transpose(grid):
    return [list(row) for row in zip(*grid)]


def invert(grid):
    return [row[::-1] for row in grid]


class Grid:
    def __init__(self, size, score=0, grid=None):
        self.size = size
        self.score = score

        if grid is None:
            self.grid = [[0 for i in range(self.size)] for j in range(self.size)]
            self.spawn()
            self.spawn()
        else:
            self.grid = grid

    def clone(self):
        return Grid(self.size, self.score, deepcopy(self.grid))

    def free_tiles(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 0]

    def spawn(self, val=None, pos=None):
        # Spawn number (random if None) on empty cell in grid
        # 90% chance for 2, 10% chance for 4
        val = val if val is not None else 2 if randrange(100) <= 90 else 4
        i, j = pos if pos is not None else choice(self.free_tiles())
        self.grid[i][j] = val

    def update(self, move):
        def move_row_left(row):
            def tighten(_row):
                # TODO: omskriv + giv credit
                # TODO: https://github.com/Fennay/python-study/blob/master/2048/2048.py

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
