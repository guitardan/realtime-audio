import numpy as np
import sounddevice as sd
import curses
from sys import stderr

def get_kick_waveform(num_samples = 1024, b_0 = 10): 
    a = num_samples//2
    x = np.arange(num_samples)
    y = np.exp(-((x-a)/b_0)**2)
    for b in [12, 15, 20, 50, 100, 200]: # kick fattening
        y += np.exp(-((x-a)/b)**2)
    return y

def get_snare_waveform(num_samples = 1024, b_0 = 50):
    a = num_samples//2
    z = np.random.randn(num_samples)
    x = np.arange(num_samples)
    return np.exp(-((x-a)/b_0)**2) + z

Fs = sd.query_devices('output')['default_samplerate']

shell = curses.initscr()
shell.nodelay(True)
curses.noecho()
curses.cbreak()
#n_rows, n_cols = shell.getmaxyx()

key_per_char = {
    'return' : 10,
    'space_bar' : 32,
    'up_arrow' : 65,
    'down_arrow' : 66
}

kick_idx, snare_idx = 0, 0
kick_on, snare_on = False, False
kick_signal, snare_signal = get_kick_waveform(), get_snare_waveform()

try:
    def callback(outdata, frames, time, status):
        if status:
            print(status, file=stderr)

        global kick_on, snare_on, kick_idx, snare_idx
        n = (kick_idx + np.arange(frames)).reshape(-1, 1)
        m = (snare_idx + np.arange(frames)).reshape(-1, 1)
        #t = (start_idx + np.arange(frames)) / Fs
        #outdata[:] = 50 * np.sin(2 * np.pi * np.sin(2 * np.pi * np.sin(2 * np.pi * f * t ) * t) * t)
        if kick_on:
            outdata[:] = kick_signal[n] # np.vstack((kick_signal[n], kick_signal[n])).T # instead of index reshape
            kick_idx += frames
        if snare_on:
            outdata[:] += snare_signal[m] 
            snare_idx += frames
        if not kick_on and not snare_on:
            outdata[:] = np.zeros((frames, 1))

        #start_idx += frames
        if kick_idx >= len(kick_signal):
            kick_on = False
            kick_idx = 0
        if snare_idx >= len(snare_signal):
            snare_on = False
            snare_idx = 0

    with sd.OutputStream(channels=2, callback=callback, samplerate=Fs): # , latency='high'
        while True:
            key = shell.getch()
            if key != -1:
                shell.erase()
                shell.addstr(0, 25, str(key), curses.A_NORMAL)
            if key == key_per_char['return']:
                #f = 2**(1/12) * f
                shell.erase()
                shell.addstr(0, 0, 'SNARE', curses.A_NORMAL)
                snare_on = True
            if key == key_per_char['space_bar']:
                shell.erase()
                shell.addstr(0, 50, 'KICK', curses.A_NORMAL)
                kick_on = True
                #f = f / 2**(1/12)

except KeyboardInterrupt:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print('keyboard interrupt')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))

class Sound():
    def __init__(self, label):
        self.is_on = False
        self.sample_idx = 0
        self
        if label == 'kick':
            self.waveform = get_kick_waveform()
            self.key_press = key_per_char['space_bar']
        elif label == 'snare':
            self.waveform = get_snare_waveform()
            self.key_press = key_per_char['return']
        print(self.waveform.shape)
        
kick_sound, snare_sound = Sound('kick'), Sound('snare') # TODO