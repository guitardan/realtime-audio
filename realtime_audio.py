import numpy as np
import sounddevice as sd
import curses
import sys

key_per_char = {
    'return' : 10,
    'space_bar' : 32,
    'up_arrow' : 65,
    'down_arrow' : 66,
    'b' : 98
    }
Fs = sd.query_devices('output')['default_samplerate']

def sine(f, t):
    return np.sin(2 * np.pi * f * t)

def get_modulated_sine(num_samples = 8192, f = 220, gain = 5):
    t = np.arange(num_samples) / Fs
    return gain * sine(sine(sine(sine(f, t) + 1, t + 2), t + 3), t)

def get_snare_waveform(num_samples = 8192):
    t = np.arange(num_samples) / Fs
    return 5 * sine(sine(sine(sine(220, t) + 1, t + 2), t + 3), t + 4)

def get_click_waveform(num_samples = 1024):
    t = np.arange(num_samples) / Fs
    return 5 * sine(sine(sine(sine(220, t) + 1, t + 2), t + 3), t + 4)

def get_hihat_waveform(num_samples = 1024, b_0 = 50):
    a = num_samples//2
    z = np.random.randn(num_samples)
    x = np.arange(num_samples)
    return np.exp(-((x-a)/b_0)**2) + z

def get_kick_waveform(num_samples = 1024, b_0 = 10): 
    a = num_samples//2
    x = np.arange(num_samples)
    y = np.exp(-((x-a)/b_0)**2)
    for b in [12, 15, 20, 50, 100, 200]: # kick fattening
        y += np.exp(-((x-a)/b)**2)
    return 10 * y

class Sound():
    def __init__(self, label):
        self.label = label
        self.is_on = False
        self.sample_index = 0
        self.label_dependent_set()

    def label_dependent_set(self):
        if self.label.lower() == 'kick':
            self.key_press = key_per_char['space_bar']
            self.waveform = get_kick_waveform()
        elif self.label.lower() == 'sine':
            self.key_press = key_per_char['down_arrow']
            self.waveform = get_modulated_sine()
        elif self.label.lower() == 'click':
            self.key_press = key_per_char['up_arrow']
            self.waveform = get_click_waveform()
        elif self.label.lower() == 'hihat':
            self.key_press = key_per_char['return']
            self.waveform = get_hihat_waveform()
        else:
            self.key_press = key_per_char['b']
            self.waveform = get_snare_waveform()

sounds = [
    Sound('CLICK'),
    Sound('HIHAT'),
    Sound('KICK'),
    Sound('SINE'),
    Sound('SNARE')
]

shell = curses.initscr()
shell.nodelay(True)
curses.noecho()
curses.cbreak()
#n_rows, n_cols = shell.getmaxyx()

try:
    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        out = np.zeros((frames, 1))
        for sound in sounds:
            if sound.is_on:
                n = (sound.sample_index + np.arange(frames)).reshape(-1, 1)
                out += sound.waveform[n]
                sound.sample_index += frames
            if sound.sample_index >= len(sound.waveform):
                sound.is_on = False
                sound.sample_index = 0
        outdata[:] = out

    with sd.OutputStream(channels=2, callback=callback, samplerate=Fs):
        while True:
            key = shell.getch()
            if key != -1:
                shell.erase()
                shell.addstr(0, 25, str(key) + ' (UNASSIGNED)', curses.A_NORMAL)
            for sound in sounds:
                if key == sound.key_press:
                    shell.erase()
                    shell.addstr(0, sound.key_press, sound.label, curses.A_NORMAL)
                    sound.is_on = True
            #f = 2**(1/12) * f # f = f / 2**(1/12)

except KeyboardInterrupt:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print('keyboard interrupt')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))