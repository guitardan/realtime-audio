import io
import numpy as np
import soundfile as sf
from urllib.request import urlopen

def print_attribution():
    name = 'Mailbox Badger : Public Domain Drum Samples : Vol. 2 (https://archive.org/details/mailboxbadgerdrumsamplesvolume2)'
    author = 'Mailbox Badger/Patrick Callan (https://archive.org/search.php?query=creator%3A%22Mailbox+Badger%2FPatrick+Callan%22)'
    license = 'CC BY 3.0 (https://creativecommons.org/licenses/by/3.0)'
    print(f'{name}\nby {author}\nis licensed under {license}.')

def get_waveforms():
    print_attribution()
    base_url = 'https://archive.org/download/mailboxbadgerdrumsamplesvolume2/Analog%20'
    indices_per_sound = {
        'Kick': np.arange(1, 5),
        'Snare': np.arange(1, 5),
        'Hihat': np.arange(1, 3),
        'Clap': np.arange(1, 2),
        'Cymbal': np.arange(1, 7),
        #'Clave': np.arange(1, 4),
        #'Conga': np.arange(1, 3),
        #'Low%20Tom' : np.arange(1, 3),
    }
    ret = []
    print('downloading samples...')
    for sound in indices_per_sound:
        #for idx in indices_per_sound[sound]:
        idx = np.random.choice(indices_per_sound[sound])
        url = f'{base_url}{sound}%20{idx}.wav'
        x, _ = sf.read(io.BytesIO(urlopen(url).read())) # TODO test MP3, OGG etc
        print(f'... {url} downloaded!')
        ret.append(x) # TODO apply linear on/off ramp
    return ret