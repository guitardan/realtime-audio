import curses
from numpy import array_equal

icon_off = [ # https://en.wikipedia.org/wiki/Box_Drawing
    '╭───────╮ ', 
    '│       │ ',
    '│       │ ',
    '╰───────╯ '
]
icon_on = [
    '╭───────╮ ',
    '│ ██ ██ │ ',
    '│ ██ ██ │ ',
    '╰───────╯ '
]
assert len(icon_off) == len(icon_on) and array_equal([len(r) for r in icon_off], [len(r) for r in icon_on])
n_group, subdivision = 4, 5
n_instruments, n_beats = 4, 16

n_rows = n_instruments * len(icon_off)
n_cols = n_beats * (len(icon_off[0]) - 1) + (subdivision * (n_beats // n_group)) - subdivision

def build_ui(stdscr):
    while True:
        maxy, maxx = stdscr.getmaxyx()
        for m in range(n_rows):
            x_gap = 0
            for n in range(n_cols):
                y = m % len(icon_off)
                x = n % len(icon_off[0])
                x_gap += subdivision if n % (len(icon_off[0]) * n_group) == 0 and n != 0 else 0
                if m >= maxy - 1 or (n + x_gap) >= maxx - 1:
                    continue
                stdscr.addstr(m, n + x_gap, icon_off[y][x], curses.A_BOLD)
                #stdscr.insstr(m, n, icon_off[m % len(icon_off)][n % len(icon_off[0])], curses.A_BOLD)

        stdscr.getch()
        stdscr.refresh()
        #stdscr.nodelay(False)
        #stdscr.erase()
        #stdscr.clear()

def main(stdscr):
    build_ui(stdscr)

curses.wrapper(main)