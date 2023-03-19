import curses
import numpy as np

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
    if key == curses.KEY_RIGHT:
        return 0, 1
    elif key == curses.KEY_LEFT:
        return 0, -1
    elif key == curses.KEY_UP:
        return -1, 0
    elif key == curses.KEY_DOWN:
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

def blink_cursor(ui_grid, ui_map, i, j, count, icon):
    if count % 2 == 0:
        ui_grid[ui_map[i, j] == ui_map] = np.array(icon.shape[0]*icon.shape[1]*[' '])
    return ui_grid

def get_active_grid(icon, on_indices):
    ui_grid, ui_map = get_grid(icon)
    for m in range(ui_grid.shape[0]):
        for n in range(ui_grid.shape[1]):
            if ui_map[m, n] in on_indices:
                ui_grid[ui_map[m, n] == ui_map] = get_icon(is_on=True).reshape(-1)
    return ui_grid, ui_map

def debug_print(stdscr, arr, vert_offset, horz_spacing = 3):
    for m in range(arr.shape[0]):
        for n in range(arr.shape[1]):
            stdscr.addstr(m + vert_offset, horz_spacing*n, str(arr[m, n]))

def debug_keys(stdscr):
    # stdscr.keypad(False)
    for key in [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT]:
        stdscr.insstr(str(key) + ' ')
    stdscr.getch()

def draw_grid(stdscr, icon, on_indices, i, j, count):
    ui_grid, ui_map = get_active_grid(icon, on_indices)
    blink_cursor(ui_grid, ui_map, i, j, count, icon)
    maxy, maxx = stdscr.getmaxyx()
    for m in range(ui_grid.shape[0]):
        for n in range(ui_grid.shape[1]):
            if m >= maxy - 1 or n >= maxx - 1:
                continue
            stdscr.addstr(m, n, ui_grid[m, n], curses.A_BOLD)
    return ui_grid, ui_map

def process_key_press(stdscr, i, j, ui_grid, ui_map, icon, on_indices):
    key = stdscr.getch()
    i, j = get_arrow_key_input(key, i, j, ui_map)
    i, j = limit_arrow_key_input(i, j, ui_grid.shape[0]-icon.shape[0], ui_grid.shape[1]-icon.shape[1])
    if key == ord(' '):
        if ui_map[i, j] in on_indices:
            sound_on[np.unravel_index(ui_map[i, j]-1, sound_on.shape)] = 0
            on_indices.remove(ui_map[i, j])
        else:
            sound_on[np.unravel_index(ui_map[i, j]-1, sound_on.shape)] = 1
            on_indices.add(ui_map[i, j])
    return i, j

def build_ui(stdscr):
    i, j, count = 0, 0, 0
    icon = get_icon()
    on_indices = set()
    while True:
        ui_grid, ui_map = draw_grid(stdscr, icon, on_indices, i, j, count)
        i, j = process_key_press(stdscr, i, j, ui_grid, ui_map, icon, on_indices)
        count += 1

        debug_print(stdscr, sound_on, ui_grid.shape[0] + 5)

        #stdscr.refresh()
        #stdscr.erase() # stdscr.clear()

n_instruments, n_beats = 4, 2
single_instrument_layout = n_beats * [1, 1, 1, 1, 0, 0, 0, 0, 0]
layout = np.vstack([single_instrument_layout for _ in range(n_instruments)])
sound_on = np.zeros((n_instruments, single_instrument_layout.count(1)), dtype=int)

def main(stdscr):
    stdscr.nodelay(True)
    stdscr.keypad(True)

    build_ui(stdscr)

curses.wrapper(main)