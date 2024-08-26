import tkinter as tk
import numpy as np
from read_board import *
from agent import *
import threading
import time
from solver import *
from agent import *
from tkinter import PhotoImage

# =====================================================================================
SCREEN_HEIGHT, SCREEN_WIDTH = 560, 480
BOARD_HEIGHT = BOARD_WIDTH = SCREEN_WIDTH

BOARD_SIZE = 9
BOARD_SIZE_SR = 3
CELL_WIDTH = BOARD_WIDTH/BOARD_SIZE

TEXT_SIZE = 11
TEXT_FONT = 'Android Assassin'
NUM_FONT = 'Robot reavers'

FONT_LIST = ['Android 101', 'Renvem italic', 'Robot reavers', 'Android Assassin']

DELAY = 200 # ms

BACKGROUND_COLOR = 'SlateGray1'
CLICKED_COLOR = 'LightSkyBlue'
LINE_COLOR = 'Black'
PROBLEM_TEXT_COLOR = 'Black'
SOLUTION_TEXT_COLOR = '#0d6b5a'
AGENT_BG_COLOR = '#52bdeb'
# =====================================================================================
START = 0
READ_BOARD = 1
CANNOT_DETECT_BOARD = 2
CHECK_BOARD = 3
FIND_SOLUTION = 4
CANNOT_SOLVE = 5
SHOW_SOLUTION = 6
FILL_SOLUTION = 7
state_text = {START : 'Click here to start',
              READ_BOARD : 'Reading board',
              CANNOT_DETECT_BOARD : 'Can\'t detect board, try again',
              CHECK_BOARD : 'If ok, click here to solve',
              FIND_SOLUTION : 'Computer thinking',
              CANNOT_SOLVE : 'Cannot solve, try again',
              SHOW_SOLUTION : 'Auto fill',
              FILL_SOLUTION : 'Is being filled in'}
state = START
# =====================================================================================
screen = tk.Tk()
screen.title(f'Sudoku Solver')
screen.resizable(width=False, height=False)

screen_width = screen.winfo_screenwidth()
screen_height = screen.winfo_screenheight()
center = (screen_width//2 - SCREEN_WIDTH//2, screen_height//2 - SCREEN_HEIGHT//2)
screen.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}+{center[0]}+{center[1]}')
screen.iconphoto(False, PhotoImage(file='image\\icon.png'))


canvas = tk.Canvas(screen, width = SCREEN_WIDTH, height = SCREEN_WIDTH, bg = BACKGROUND_COLOR)
canvas.place(x=0, y=0)

board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
labels = None
cells = None
last_cell = None
mask = None
# =====================================================================================
def draw_puzzle():
    global board, labels, cells, mask

    canvas.delete('all')
    labels = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    cells = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):            
            pos1 = (col*CELL_WIDTH, row*CELL_WIDTH)
            pos2 = (pos1[0]+CELL_WIDTH, pos1[1]+CELL_WIDTH)

            cell_id = canvas.create_rectangle(pos1[0], pos1[1], pos2[0], pos2[1], outline = LINE_COLOR)
            cells[row][col] = cell_id
            
            if type(mask) == np.ndarray and mask[row, col] == 0:
                current_fg = SOLUTION_TEXT_COLOR
            else: current_fg = PROBLEM_TEXT_COLOR

            value = board[row, col] if board[row, col] != 0 else ''
            label = tk.Label(canvas, text = value, font = (NUM_FONT, TEXT_SIZE, 'bold'), bg = BACKGROUND_COLOR, fg = current_fg)

            center = (col*CELL_WIDTH + CELL_WIDTH/2, row*CELL_WIDTH + CELL_WIDTH/2)
            label_id = canvas.create_window(center[0], center[1], window=label, anchor = 'center')
            labels[row][col] = label
    draw_big_square()

def draw_big_square():
    for row in range(BOARD_SIZE_SR):
        for col in range(BOARD_SIZE_SR):
            pos1 = (col*BOARD_SIZE_SR*CELL_WIDTH, row*BOARD_SIZE_SR*CELL_WIDTH)
            pos2 = (pos1[0] + BOARD_SIZE_SR*CELL_WIDTH, pos1[1] + BOARD_SIZE_SR*CELL_WIDTH)
            canvas.create_rectangle(pos1[0], pos1[1], pos2[0], pos2[1], outline = LINE_COLOR, width = 2)

def reset(reset_board=True):
    global last_cell, labels, cells, board

    if last_cell != None:
        canvas.itemconfig(cells[last_cell[0]][last_cell[1]], fill = BACKGROUND_COLOR)
        labels[last_cell[0]][last_cell[1]].config(bg = BACKGROUND_COLOR)

    last_cell = labels = cells = mask = None
    if reset_board:
        board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        update_agent(START)
    else: update_agent(state)
    draw_puzzle()
# =====================================================================================
def handle_mouse_click(event):
    global last_cell, cells, labels

    pos = (event.x, event.y)
    coord = (pos[1]*BOARD_SIZE//BOARD_HEIGHT, pos[0]*BOARD_SIZE//BOARD_WIDTH)

    if last_cell != None:
        canvas.itemconfig(cells[last_cell[0]][last_cell[1]], fill = BACKGROUND_COLOR)
        labels[last_cell[0]][last_cell[1]].config(bg = BACKGROUND_COLOR)
    
    last_cell = coord
    canvas.itemconfig(cells[last_cell[0]][last_cell[1]], fill = CLICKED_COLOR)
    labels[last_cell[0]][last_cell[1]].config(bg = CLICKED_COLOR)       

def handle_keyboard(event):
    global state, board

    key = event.keysym.lower()
    if key == 'r': 
        reset(reset_board=True)
    elif last_cell != None: 
        value = None
        if '1' <= key <= '9': 
            value = int(key)
        elif key == 'backspace':
            value = ''

        if value is not None:
            label = labels[last_cell[0]][last_cell[1]]
            label.config(text=value)
            
            if value == '': 
                value = 0
            board[last_cell[0], last_cell[1]] = value

            draw_big_square()
    
canvas.bind('<Button-1>', handle_mouse_click) # left mouse click
screen.bind("<KeyPress>", handle_keyboard) # keyboard input
#=====================================================================================
origin = None
cell_width = None

def take_screenshort():
    screen.iconify()
    time.sleep(0.25)

    screenshort = pyautogui.screenshot()
    screen.deiconify()

    return np.array(screenshort)

def take_board(queue=Queue(), counter=0):
    global board, origin, cell_width

    if not queue.empty():
        (origin, cell_width), board = queue.get()
        if type(board) != np.ndarray:
            board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.ndarray)
            update_agent(CANNOT_DETECT_BOARD)
        else:
            reset(reset_board=False)
            update_agent(CHECK_BOARD)
    else:
        if counter==0:
            screenshort = take_screenshort()
            run_thread(func=get_board, args=(screenshort, queue))

        update_agent(READ_BOARD, counter)
        screen.after(DELAY, take_board, queue, counter+1)  
#=====================================================================================
def get_solution(queue=Queue(), counter=0):
    global board, mask

    if not queue.empty():
        solution = queue.get()
        if type(solution) != np.ndarray: # cannot use not solution because solution can np.array
            update_agent(CANNOT_SOLVE)
        else:
            update_agent(SHOW_SOLUTION)
            mask = board
            board = solution
            reset(reset_board=False)
            draw_puzzle(mask)
    else:
        if counter==0:
            run_thread(func=solver, args=(board, queue))
        
        update_agent(FIND_SOLUTION, counter)
        screen.after(DELAY, get_solution, queue, counter+1)
#=====================================================================================
def auto_fill(is_done=threading.Event(), counter=0):
    global mask, board

    if is_done.is_set():
        reset()
    else:
        if counter==0:
            run_thread(func=start_agent, args=(is_done,))

        update_agent(FILL_SOLUTION, counter)
        screen.after(DELAY, auto_fill, is_done, counter+1)

def start_agent(is_done : threading.Event):
    global mask, board

    agent = Agent(origin, cell_width)

    rows, cols = np.nonzero(mask==0)
    blank_cells = list(zip(rows, cols))
    np.random.shuffle(blank_cells)

    for cell in blank_cells:
        agent.fill(cell, board[cell])
    is_done.set()

#=====================================================================================
def call_agent():
    global state

    if state == START or state == CANNOT_DETECT_BOARD:
        run_thread(func=take_board)
    elif state == CHECK_BOARD or state == CANNOT_SOLVE:
        run_thread(func=get_solution)
    elif state == SHOW_SOLUTION:
        run_thread(func=auto_fill)

def update_agent(new_state, suffix_len=0):
    global state

    state = new_state
    new_text = state_text[new_state] + '. '*(suffix_len%4)
    agent_button.config(text = new_text, font = (TEXT_FONT, TEXT_SIZE, 'bold'))

def run_thread(func, args=()):
    threading.Thread(target=func, args=args).start()
#=====================================================================================
agent_button = tk.Button(screen, text = state_text[state], bd = 1, relief = 'solid', bg = AGENT_BG_COLOR, command=call_agent)
agent_button.place(x = 0, y = 480, width = 480, height = 60)
#=====================================================================================
menubar = tk.Menu(screen)
screen.config(menu=menubar)

def change_font(new_font):
    global TEXT_FONT

    TEXT_FONT = new_font
    reset(reset_board=False)

setting_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Setting', menu=setting_menu)

text_font_menu = tk.Menu(setting_menu, tearoff=0)
setting_menu.add_cascade(label='Text font', menu=text_font_menu)

for font in FONT_LIST:
    text_font_menu.add_command(label=font, command=lambda f=font : change_font(f))
#=====================================================================================


if __name__ == '__main__':
    reset()
    screen.mainloop()