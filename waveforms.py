import numpy as np

def sine(f, t):
    return np.sin(2 * np.pi * f * t)

def get_modulated_sine(Fs, num_samples = 8192, f = 220, gain = 5):
    t = np.arange(num_samples) / Fs
    #f = 2**(1/12) * f
    return gain * sine(sine(sine(sine(f, t) + 1, t + 2), t + 3), t)

def get_snare(Fs, num_samples = 8192):
    t = np.arange(num_samples) / Fs
    return 5 * sine(sine(sine(sine(220, t) + 1, t + 2), t + 3), t + 4)

def get_click(Fs, num_samples = 1024):
    t = np.arange(num_samples) / Fs
    return 5 * sine(sine(sine(sine(220, t) + 1, t + 2), t + 3), t + 4)

def get_hihat(num_samples = 1024, b_0 = 100):
    a = num_samples//2
    z = np.random.randn(num_samples)
    x = np.arange(num_samples)
    return 10 * np.exp(-((x-a)/b_0)**2) + z

def get_kick(num_samples = 1024, b_0 = 10): 
    a = num_samples//2
    x = np.arange(num_samples)
    y = np.exp(-((x-a)/b_0)**2)
    for b in [12, 15, 20, 50, 100, 200]: # kick fattening
        y += np.exp(-((x-a)/b)**2)
    return 10 * y