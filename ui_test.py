import curses
import numpy as np

key_per_char = {
    'down_arrow' : 258,
    'up_arrow' : 259,
    'left_arrow' : 260,
    'right_arrow' : 261
    }

def compute(vals):
    num_samples = sum([v for v in vals])**2
    pos_samples = sum([v**2 for v in vals])
    print(f'{pos_samples}/{num_samples} = {pos_samples/num_samples}')

def blink(stdscr, i, j, count, marker):
    stdscr.addstr(i, j, f'{marker}' if count % 2 == 0 else len(str(marker))*' ')

def generate_noise(stdscr, char = '█'):
    count = 0
    while True:
        maxy, maxx = stdscr.getmaxyx()
        i, j = np.random.randint(maxy-1), np.random.randint(maxx-1)
        blink(stdscr, i, j, count, char)
        stdscr.refresh()
        count += 1

def get_arrow_key_input(key, i, j, i_step = 1, j_step = 1):
    if key == key_per_char['right_arrow']:
        j += j_step
    if key == key_per_char['left_arrow']:
        j -= j_step
    if key == key_per_char['up_arrow']:
        i -= i_step
    if key == key_per_char['down_arrow']:
        i += i_step
    return i, j

def process_arrow_key_input(key, i, j, max_i, max_j, i_step = 1, j_step = 1):
    i, j = get_arrow_key_input(key, i, j, i_step=i_step, j_step=j_step)
    if i < 0:
        i = 0
    if j < 0:
        j = 0
    if i >= max_i:
        i = max_i - 1
    if j >= max_j:
        j = max_j - 1
    return i, j

def get_test_icon(m, n, m_i, m_f, n_i, n_f):
    icon_off = [
        '╭──╮ ', 
        '╰──╯ '
    ]
    icon_on = [
        '╭||╮ ', 
        '╰||╯ '
    ]
    assert len(icon_off) == len(icon_on) and np.array_equal([len(r) for r in icon_off], [len(r) for r in icon_on])
    if m_i < m and m < m_f and n_i < n and n < n_f:
        return icon_on
    else:
        return icon_off

def test_ui(stdscr):
    n_group, subdivision = 4, 5
    n_rows, n_cols = 6, 19
    i, j = 0, 0
    while True:
        maxy, maxx = stdscr.getmaxyx()
        for m in range(n_rows):
            n_gap = 0
            for n in range(n_cols):
                icon = get_test_icon(m, n, i, i+3, j, j+5)
                y = m % len(icon)
                x = n % len(icon[0])
                n_gap += subdivision if n % (len(icon[0]) * n_group) == 0 and n != 0 else 0

                if m >= maxy - 1 or (n + n_gap) >= maxx - 1:
                    continue
                stdscr.addstr(m, n + n_gap, icon[y][x], curses.A_BOLD)
        key = stdscr.getch()
        i, j = process_arrow_key_input(key, i, j, maxy, maxx, 2, 4)
        stdscr.refresh()

def get_icon():
    icon_off = np.array([ # https://en.wikipedia.org/wiki/Box_Drawing
        ['╭', '─', '─', '─', '─', '─', '╮', ' '], 
        ['│', ' ', ' ', ' ', ' ', ' ', '│', ' '],
        ['╰', '─', '─', '─', '─', '─', '╯', ' ']
    ])
    icon_on = np.array([
        ['╭', '─', '─', '─', '─', '─', '╮', ' '],
        ['│', ' ', '█', '█', '█', ' ', '│', ' '],
        ['╰', '─', '─', '─', '─', '─', '╯', ' ']
    ])
    assert len(icon_off) == len(icon_on) and np.array_equal([len(r) for r in icon_off], [len(r) for r in icon_on])
    return icon_off

def get_grid_and_mapping(layout, icon):
    idx = 1 # using 0 for gaps
    hgap = ' ' * np.ones((icon.shape[0], 1), dtype=object)
    grid_out, grid_map = [], []
    for layout_row in layout:
        # if (layout_row == 0).all(): # TODO
        #     grid_out.append(len(layout_row) * list(vgap[0]))
        #     grid_map.append(np.zeros((1, len(layout_row) * vgap.shape[1])))
        #     continue
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
    return np.vstack(grid_out), np.vstack(grid_map).astype(int)

def render(stdscr, grid):
    stdscr.nodelay(False)
    line_idx = 0
    for row in grid:
        line = ''
        for s in row:
            line += str(s)
        stdscr.addstr(line_idx, 0, line, curses.A_BOLD)
        line_idx += 1
    stdscr.getch()

def build_ui(stdscr):
    layout = np.array([
        [1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1,],
        [1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1],
        [1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1],
        [1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1]
        ])
    ui_grid, ui_map = get_grid_and_mapping(layout, get_icon())
    render(stdscr, ui_grid)

def main(stdscr):
    stdscr.nodelay(True)
    #stdscr.keypad(False)

    #generate_noise(stdscr, '❤️')
    #test_ui(stdscr)
    build_ui(stdscr)

curses.wrapper(main)