import curses
import numpy as np

key_per_char = {
    'down_arrow' : 258,
    'up_arrow' : 259,
    'left_arrow' : 260,
    'right_arrow' : 261
    }

key_per_char = {
    'return' : 10,
    'space_bar' : 32,
    'up_arrow' : 65,
    'down_arrow' : 66,
    'right_arrow' : 67,
    'left_arrow' : 68,
    'b' : 98
    }

n_instruments, n_beats = 4, 2
single_instrument_layout = n_beats * [1, 1, 1, 1, 0, 0, 0, 0, 0]
layout = np.vstack([single_instrument_layout for _ in range(n_instruments)])

def get_grid(icon):
    hgap = ' ' * np.ones((icon.shape[0], 1), dtype=object)
    idx = 1 # using 0 for gaps
    grid_out, grid_map = [], []
    for layout_row in layout:
        out_row, map_row = [], []
        for layout_val in layout_row:
            if layout_val == 1:
                out_row.append(icon)
                map_row.append(idx * np.ones(icon.shape))
                idx += 1
            else:
                out_row.append(hgap)
                map_row.append(np.zeros((len(hgap), 1)))
        grid_out.append(np.hstack(out_row))
        grid_map.append(np.hstack(map_row))
    grid_out = np.vstack(grid_out)
    grid_map = np.vstack(grid_map).astype(int)
    assert grid_out.shape == grid_map.shape
    return grid_out, grid_map

def get_icon(is_on = False):
    icon_on = np.array([
        ['╭', '─', '─', '─', '─', '-', '╮', ' '],
        ['│', ' ', '█', '█', '█', ' ', '│', ' '],
        ['╰', '─', '─', '─', '─', '─', '╯', ' ']
    ])
    icon_off = np.array([
        ['╭', '─', '─', '─', '─', '─', '╮', ' '], 
        ['│', ' ', ' ', ' ', ' ', ' ', '│', ' '],
        ['╰', '─', '─', '─', '─', '─', '╯', ' ']
    ])
    assert icon_on.shape == icon_off.shape
    if is_on:
        return icon_on
    return icon_off

def blink_cursor(stdscr, i, j, count, marker):
    stdscr.addstr(i, j, f'{marker}' if count % 2 == 0 else len(str(marker))*' ')

def get_arrow_key_input(key, i, j, grid_map):
    idx = grid_map[i, j]
    i_step, j_step = get_steps(key)
    if (i_step == 0 and j_step == 0):
        return i, j # no arrow key pressed
    try:
        while (grid_map[i, j] == idx or grid_map[i, j] == 0):
            i += i_step
            j += j_step
        return i, j
    except IndexError:
        return i, j

def get_steps(key):
    if key == key_per_char['right_arrow']:
        return 0, 1
    elif key == key_per_char['left_arrow']:
        return 0, -1
    elif key == key_per_char['up_arrow']:
        return -1, 0
    elif key == key_per_char['down_arrow']:
        return 1, 0
    else:
        return 0, 0
    
def limit_arrow_key_input(i, j, max_i, max_j):
    if i < 0:
        i = 0
    if j < 0:
        j = 0
    if i >= max_i:
        i = max_i
    if j >= max_j:
        j = max_j
    return i, j

def build_ui(stdscr):
    i, j, count = 0, 0, 0
    icon = get_icon()
    while True:
        ui_grid, ui_map = get_grid(icon)
        ui_grid[ui_map[i, j] == ui_map] = get_icon(is_on=True).reshape(-1)
        maxy, maxx = stdscr.getmaxyx()
        for m in range(ui_grid.shape[0]):
            for n in range(ui_grid.shape[1]):
                if m >= maxy - 1 or n >= maxx - 1:
                    continue
                stdscr.addstr(m, n, ui_grid[m, n], curses.A_BOLD) # stdscr.insstr()
        count += 1
        key = stdscr.getch()
        i, j = get_arrow_key_input(key, i, j, ui_map)
        i, j = limit_arrow_key_input(i, j, ui_grid.shape[0]-icon.shape[0], ui_grid.shape[1]-icon.shape[1])

        stdscr.refresh()
        #stdscr.erase()
        #stdscr.clear()

def main(stdscr):
    stdscr.nodelay(True)
    stdscr.keypad(False)
    build_ui(stdscr)

curses.wrapper(main)