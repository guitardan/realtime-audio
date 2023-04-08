import numpy as np
import sounddevice as sd
from curses import wrapper

def noisy_sinc(f_0 = 220, dur_s = 1.125, sr = 44100):
    t = np.arange(1, sr * dur_s + 1) / sr
    sinc = np.sin(np.pi * f_0 * t) / t
    return 0.001 * np.random.randn(len(sinc)) * sinc

def osc(f_0 = 220, dur_s = 1, sr = 44100):
    t = np.arange(sr * dur_s) / sr
    return np.sin(np.pi * f_0 * t)

def lfo_modulate(power = 3, iter = 10, x = osc()):
    for i in range(1, iter):
        x = x * osc(i**power)
    return x

def get_sample_onsets():
    ret = np.zeros((subdiv_ons.shape[0], n_subdiv*subdiv_ons.shape[1]))
    return ret

def get_superposition():
    out = np.zeros((subdiv_ons.shape[0], n_subdiv*subdiv_ons.shape[1]))
    for m in range(subdiv_ons.shape[0]):
        for n in range(subdiv_ons.shape[1]):
            if subdiv_ons[m, n] == 1:
                if n_subdiv*n+len(waveforms[m]) > n_subdiv*(n+1):
                    out[m, n_subdiv*n : n_subdiv*(n+1)] += waveforms[m][:n_subdiv]
                else:
                    out[m, n_subdiv*n : n_subdiv*n+len(waveforms[m])] += waveforms[m]
    return out

def is_ui_running(stdscr):
    global subdiv_ons
    idx = 2
    for r in subdiv_ons:
        stdscr.addstr(idx, 0, str(r))
        idx += 1
    stdscr.refresh()
    key = stdscr.getch()
    if key == ord('q'):
        stream.stop()
        return False
    elif key == ord('s'):
        subdiv_ons = np.random.randint(low=0, high=2, size=subdiv_ons.shape)
    return True

def run_ui(stdscr):
    while True:
        if not is_ui_running(stdscr):
            break

def main(stdscr, is_threaded = True):
    stdscr.addstr(0, 0, "Press 'q' to quit")
    stdscr.addstr(1, 0, "Press 's' to shuffle sounds")
    if is_threaded:
        import threading
        threading.Thread(target=play_audio).start()
        run_ui(stdscr)
    else:
        with stream:
            run_ui(stdscr)

def play_audio():
    with stream:
        while True:
            if stream.stopped:
                break

idx = 0
def callback(outdata, frames, time, status):
    global idx
    output_signal = get_superposition().sum(axis=0).reshape(-1, 1) # waveforms[0].reshape(-1, 1)
    outdata[:] = output_signal[idx:idx+frames]
    idx += frames
    if idx > len(output_signal)-frames:
        idx = 0

n_channels = 2
samplerate = sd.query_devices('output')['default_samplerate']
stream = sd.OutputStream(channels=n_channels, callback=callback, samplerate=samplerate)

waveforms = [
    noisy_sinc(f_0 = 220, dur_s = 1.25, sr = samplerate),
    lfo_modulate(),
    lfo_modulate(4, 8)
    ]

subdiv_ons = np.array([
    [0,1,0,1],
    [1,1,1,1],
    [1,0,1,0]
    ])
n_subdiv = int(samplerate // 2) # 120 BPM
out = get_superposition()

#import matplotlib.pyplot as plt
#%matplotlib
#plt.figure()
#plt.imshow(out, aspect='auto', origin='lower', cmap='prism')

if __name__ == '__main__':
    wrapper(main)