import pyautogui as pg
from queue import Queue
from copy import deepcopy
import numpy as np

def check_row_col(board, coor, value):
    for i in range(9):
        if board[coor[0], i] == value or board[i, coor[1]] == value:
            return False
    return True

def check_square(board, coord, value):
    sx, sy = int(coord[0]/3)*3, int(coord[1]/3)*3
    dx = [0]*3 + [1]*3 + [2]*3
    dy = [0, 1, 2]*3

    for i, j in zip(dx, dy):
        if board[sx+i, sy+j] == value:
            return False
    return True

def is_safe(board, coord, value):
    if not check_row_col(board, coord, value) or not check_square(board, coord, value):
        return False
    return True

def find_blank(board):
    mask = (board==0)
    rows, cols = np.nonzero(mask)
    blank_cells = list(zip(rows, cols))
    return blank_cells

def solver(board, queue : Queue):
    blank_cells = find_blank(board)

    solution = solve_(board.copy(), blank_cells)
    queue.put(solution)
                    
def solve_(board, blank_cells, i=0):
    if i == len(blank_cells):
        return True
    
    for value in range(1, 10):
        if is_safe(board, blank_cells[i], value):
            board[blank_cells[i]] = value
            if solve_(board, blank_cells, i+1):
                return board if i==0 else True
            else: board[blank_cells[i]] = 0
    return False