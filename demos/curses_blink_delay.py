import curses

def getstr(w, y, x):
    window = curses.newwin(1, w, y, x)

    result = ""
    window.addstr("> ", curses.A_BOLD + curses.A_BLINK)
    window.refresh()
    window.keypad(True)

    while True:
        try:
            character = -1
            while (character < 0):
                character = window.getch()
        except:
            break

        if character == curses.KEY_ENTER or character == ord('\n'):
            break

        elif character == curses.KEY_BACKSPACE or character == 127:
            if len(result):
                window.move(0, len(result)+1)
                window.delch()
                result = result[:-1]
                continue

        elif (137 > character > 31 and len(result) < w-3): # ascii range TODO: unicode
                result += chr(character)
                window.addstr(chr(character))

    window.addstr(0, 0, "> ", curses.A_BOLD + curses.color_pair(3))
    window.refresh()

    window.keypad(False)
    return result

def ui(stdscr, char = '~'):
    curses.curs_set(0)
    for m in range(5): # draw once
        for n in range(10):
            stdscr.addstr(m, n, char)
    i, j = 0, 0
    while True:
        stdscr.addstr(i, j, char, curses.A_BLINK)
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            stdscr.addstr(i, j, char) # clear previous blink
            j -= 1
        elif key == curses.KEY_RIGHT:
            stdscr.addstr(i, j, char)
            j += 1
        elif key == curses.KEY_UP:
            stdscr.addstr(i, j, char)
            i -= 1
        elif key == curses.KEY_DOWN:
            stdscr.addstr(i, j, char)
            i += 1


def main(stdscr):
    #stdscr.nodelay(True)
    stdscr.keypad(True)
    try:
        ui(stdscr)
        #getstr(0, 0, 0)
    except KeyboardInterrupt:
        curses.nocbreak()
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)