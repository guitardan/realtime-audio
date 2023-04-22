import sys, curses, threading
import numpy as np
import sounddevice as sd
from . import waveforms as wfs
import time

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
        ['╭', ' ', '-', ' ', '-', ' ', '╮', ' '],
        [' ', ' ', '█', '█', '█', ' ', ' ', ' '],
        ['╰', ' ', '-', ' ', '-', ' ', '╯', ' ']
    ])
    icon_off = np.array([
        ['╭', ' ', '-', ' ', '-', ' ', '╮', ' '], 
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['╰', ' ', '-', ' ', '-', ' ', '╯', ' ']
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

def blink_cursor(ui_grid, ui_map, i, j, icon, period_s = 0.25):
    if time.time() % period_s < period_s / 2:
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

def draw_grid(stdscr, icon, on_indices, i, j):
    ui_grid, ui_map = get_active_grid(icon, on_indices)
    blink_cursor(ui_grid, ui_map, i, j, icon)
    maxy, maxx = stdscr.getmaxyx()
    cidx = 0
    for m in range(ui_grid.shape[0]):
        if curses.has_colors() and m % icon.shape[0] == 0 and 0 < m:
            cidx += 1
        for n in range(ui_grid.shape[1]):
            if m >= maxy - 1 or n >= maxx - 1:
                continue
            stdscr.addstr(m, n, ui_grid[m, n], curses.color_pair(instr_color_idx[cidx]) if curses.has_colors() else curses.A_BOLD)

    return ui_grid, ui_map

def process_key_press(stdscr, i, j, ui_grid, ui_map, icon, on_indices, tempo_delta_samples = 100):
    global n_subdiv_samples, sound_on
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
    elif key == ord('='):
        n_subdiv_samples -= tempo_delta_samples
        if n_subdiv_samples <= 0:
            n_subdiv_samples += 2*tempo_delta_samples
    elif key == ord('-'):
        n_subdiv_samples += tempo_delta_samples
    elif key == ord('r'):
        sound_on = np.random.randint(low=0, high=2, size=(n_instruments, single_instrument_layout.count(1)))
    return i, j

def get_indices():
    idx_i, row_idx = 1, 0
    indices = set()
    for row in sound_on:
        indices.update(np.where(row == 1)[0] + idx_i + row_idx)
        row_idx += len(row)
    return indices

def display_help(stdscr, y0):
    stdscr.addstr(y0 + 1, 0, 'MOVE CURSOR: ← / ↑ / → / ↓')
    stdscr.addstr(y0 + 2, 0, '(DE)ACTIVATE SOUND: <spacebar>')
    stdscr.addstr(y0 + 3, 0, 'CHANGE TEMPO: + / -')
    stdscr.addstr(y0 + 4, 0, 'RANDOM BEAT: R')
    stdscr.addstr(y0 + 5, 0, 'EXIT: CTRL + C')

def build_ui(stdscr):
    i, j = 0, 0
    icon = get_icon()
    threading.Thread(target=play_audio).start()

    while True:
        on_indices = get_indices()
        ui_grid, ui_map = draw_grid(stdscr, icon, on_indices, i, j)
        i, j = process_key_press(stdscr, i, j, ui_grid, ui_map, icon, on_indices)

        #debug_print(stdscr, sound_on, ui_grid.shape[0] + 5)
        display_help(stdscr, ui_grid.shape[0])
        stdscr.refresh() # stdscr.erase() # stdscr.clear()

def get_superposition():
    out = np.zeros((sound_on.shape[0], n_subdiv_samples*sound_on.shape[1]))
    for m in range(sound_on.shape[0]):
        for n in range(sound_on.shape[1]):
            if sound_on[m, n] == 1:
                if n_subdiv_samples*n+len(waveforms[m]) > n_subdiv_samples*(n+1):
                    out[m, n_subdiv_samples*n : n_subdiv_samples*(n+1)] += waveforms[m][:n_subdiv_samples]
                else:
                    out[m, n_subdiv_samples*n : n_subdiv_samples*n+len(waveforms[m])] += waveforms[m]
    return out

def play_audio():
    with stream:
        while True:
            if stream.stopped:
                break

def get_samplerate():
    output_device = sd.query_devices(kind='output')
    try:
        return output_device['default_samplerate']
    except TypeError:
        print('no output device available, terminating...')
        sys.exit(0)
    except KeyError:
        print('no default samplerate available, terminating...')
        sys.exit(0)

def init_colors(stdscr=None):
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        try:
            curses.init_pair(i + 1, i, -1)
        except ValueError:
            break
    if stdscr:
        stdscr.nodelay(False)
        for i in range(0, 255):
            stdscr.addstr(f'{i} ', curses.color_pair(i))
        stdscr.getch()
        stdscr.nodelay(True)
        stdscr.erase()

idx = 0
def callback(outdata, frames, time, status):
    global idx
    try:
        output_signal = get_superposition().sum(axis=0).reshape(-1, 1)
        outdata[:] = gain * output_signal[idx:idx+frames]
        idx += frames
        if idx > len(output_signal)-frames:
            idx = 0
    except ValueError: # extreme tempo changes
        outdata[:] = np.zeros((frames,1))

n_instruments, n_beats = 4, 4
instr_color_idx = [14, 4, 11, 7]
single_instrument_layout = n_beats * [1, 1, 1, 1, 0, 0, 0, 0]
layout = np.vstack([single_instrument_layout for _ in range(n_instruments)])
sound_on = np.zeros((n_instruments, single_instrument_layout.count(1)), dtype=int)

gain = 0.01
n_channels = 2
samplerate = get_samplerate()
stream = sd.OutputStream(channels=n_channels, callback=callback, samplerate=samplerate)

n_subdiv_samples = int(samplerate // 8) # 120 BPM, 16th note subdiv
waveforms = [
    wfs.get_kick(),
    wfs.get_snare(Fs=samplerate),
    wfs.get_hihat(),
    wfs.get_click(Fs=samplerate),
    wfs.get_modulated_sine(Fs=samplerate)
]

def main(stdscr):
    stdscr.nodelay(True)
    stdscr.keypad(True)
    if curses.has_colors():
        init_colors() # stdscr) # 
    try:
        build_ui(stdscr)
    except KeyboardInterrupt:
        stream.stop()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

#sys.exit(0)
if __name__ == "__main__":
    curses.wrapper(main)