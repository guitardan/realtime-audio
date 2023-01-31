import numpy as np
import sounddevice as sd
import sys, curses, waveforms
from curses import wrapper

if len(sys.argv) > 1:
    is_sequencer = False
    print('running as sample trigger, press ENTER to continue...')
    input()
else:
    is_sequencer = True
    print('running as sequencer, press ENTER to continue...')
    input()
n_beats = 16
n_instruments = 4
labels = ['KICK', 'HIHAT', 'SNARE', 'CLICK']
period = 1e3 # produce reasonable BPM
gain = 0.1
marker = '.'

key_per_char = {
    'return' : 10,
    'space_bar' : 32,
    'up_arrow' : 65,
    'down_arrow' : 66,
    'right_arrow' : 67,
    'left_arrow' : 68,
    'b' : 98
    }

Fs = sd.query_devices('output')['default_samplerate']

class Sound():
    def __init__(self, label, period = period, shift = 0, is_on = False):
        self.label = label
        self.is_on = is_on
        self.sample_index = 0
        self.is_quantized_on = False
        self.period = period
        self.shift = shift
        self.label_dependent_set()

    def label_dependent_set(self):
        if self.label.lower() == 'kick':
            self.key_press = key_per_char['space_bar']
            self.waveform = waveforms.get_kick()
            #self.period = 2 * self.period
        elif self.label.lower() == 'snare':
            self.key_press = key_per_char['b']
            self.waveform = waveforms.get_snare(Fs)
            #self.shift = 2 * self.period
            #self.period = 4 * self.period
        elif self.label.lower() == 'sine':
            self.key_press = key_per_char['down_arrow']
            self.waveform = waveforms.get_modulated_sine(Fs)
        elif self.label.lower() == 'click':
            self.key_press = key_per_char['up_arrow']
            self.waveform = waveforms.get_click(Fs)
        else:
            self.key_press = key_per_char['return']
            self.waveform = waveforms.get_hihat()

if is_sequencer:
    sounds = []
else:
    sounds = [
        Sound('CLICK'),
        Sound('HIHAT'),
        Sound('KICK'),
        Sound('SINE'),
        Sound('SNARE')
    ]

stdscr = curses.initscr()
stdscr.nodelay(True)
curses.noecho()
curses.cbreak()
n_rows, n_cols = stdscr.getmaxyx()

def process_arrow_key_input(key, i, j):
    if key == key_per_char['right_arrow']:
        j += 1
    if key == key_per_char['left_arrow']:
        j -= 1
    if key == key_per_char['up_arrow']:
        i -= 1
    if key == key_per_char['down_arrow']:
        i += 1
    return i, j

def limit_to_grid(i, j):
    if i < 0:
        i = 0
    if j < 0:
        j = 0
    if i >= grid.shape[0]:
        i = grid.shape[0] - 1
    if j >= grid.shape[1]:
        j = grid.shape[1] - 1
    return i, j

def update_grid():
    for m in range(grid.shape[0]):
        for n in range(grid.shape[1]):
            if m == i and n == j and grid[i, j] == 0:
                continue
            if grid[m, n] == 1: # keep on
                stdscr.addstr(m, n, marker, curses.A_BOLD)
            else:
                stdscr.addstr(m, n, '_', curses.A_BOLD)

def remove_off(sounds):
    out = []
    for s in sounds:
        if s.label == labels[i] and s.shift == j*period:
            continue
        out.append(s)
    return out

def process_key_press(sounds):
    if grid[i, j] == 1: # turn off
        stdscr.addstr(i, j, '_', curses.A_BOLD)
        grid[i, j] = 0
        sounds = remove_off(sounds)
    else:
        stdscr.addstr(i, j, marker, curses.A_BOLD)
        grid[i, j] = 1
        sounds.append(Sound(
                labels[i],
                period=grid.shape[1]*period, # period, # 
                shift=j*period, # 0, # 
                is_on=True))
    return sounds

def blink_cursor():
    if grid[i, j] == 1:
        stdscr.addstr(i, j, marker if count % 2 == 0 else ' ', curses.A_BOLD)
    else:
        stdscr.addstr(i, j, '_' if count % 2 == 0 else ' ', curses.A_BOLD)

try:
    def callback(outdata, frames, time, status):
        if status:
            stdscr.addstr(grid.shape[0], grid.shape[1], str(status), curses.A_BOLD)

        out = np.zeros((frames, 1))
        for sound in sounds:
            sound_on = sound.is_quantized_on if is_sequencer else sound.is_on
            if sound_on:
                n = (sound.sample_index + np.arange(frames)).reshape(-1, 1)
                out += sound.waveform[n]
                sound.sample_index += frames

            if sound.sample_index >= len(sound.waveform):
                if is_sequencer:
                    sound.is_quantized_on = False
                else:
                    sound.is_on = False
                sound.sample_index = 0

        outdata[:] = gain * out

    with sd.OutputStream(channels=2, callback=callback, samplerate=Fs):
        count, i, j = 0, 0, 0
        grid = np.zeros((n_instruments, n_beats))

        while True:
            key = stdscr.getch()

            for sound in sounds:
                if is_sequencer:
                    if count % sound.period == sound.shift and sound.is_on:
                        sound.is_quantized_on = True
                elif key == sound.key_press:
                    stdscr.erase()
                    stdscr.addstr(0, sound.key_press if sound.key_press < n_cols else n_cols - len(sound.label), sound.label, curses.A_NORMAL)
                    sound.is_on = True

            if not is_sequencer:
                continue

            update_grid()
            if key == key_per_char['space_bar']:
                sounds = process_key_press(sounds)
            else:
                blink_cursor()

            i, j = process_arrow_key_input(key, i, j)
            i, j = limit_to_grid(i, j)

            # if key != -1:
            #     shell.erase()
            #     shell.addstr(0, 25, str(key) + ' (UNASSIGNED)', curses.A_NORMAL)

            count += 1

except KeyboardInterrupt:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print('keyboard interrupt')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))