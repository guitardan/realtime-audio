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
    #f = 2**(1/12) * f
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
        self.is_quantized_on = False
        self.period = 1e5
        self.shift = 0
        self.label_dependent_set()

    def label_dependent_set(self):
        if self.label.lower() == 'kick':
            self.key_press = key_per_char['space_bar']
            self.waveform = get_kick_waveform()
            self.period = 2 * self.period
        elif self.label.lower() == 'snare':
            self.key_press = key_per_char['b']
            self.waveform = get_snare_waveform()
            self.shift = 2 * self.period
            self.period = 4 * self.period
        elif self.label.lower() == 'sine':
            self.key_press = key_per_char['down_arrow']
            self.waveform = get_modulated_sine()
        elif self.label.lower() == 'click':
            self.key_press = key_per_char['up_arrow']
            self.waveform = get_click_waveform()
        else:
            self.key_press = key_per_char['return']
            self.waveform = get_hihat_waveform()

sounds = [
    Sound('CLICK'),
    Sound('HIHAT'),
    Sound('KICK'),
    Sound('SINE'),
    Sound('SNARE')
]
is_sequencer = True # False

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

        outdata[:] = 0.1 * out

    with sd.OutputStream(channels=2, callback=callback, samplerate=Fs):
        count = 0
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
                    count = 1

                if count % sound.period == sound.shift and sound.is_on:
                    sound.is_quantized_on = True

            count += 1

except KeyboardInterrupt:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print('keyboard interrupt')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))