import io
import os 
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

def get_waveforms_local(directory_path, file_names=None):
    """
    Load and return a set of waveforms from .wav files in a specified directory.

    This function reads specified .wav files from the given directory and returns their waveforms
    as a list of numpy arrays. Only mono waveforms are accepted. 
    If no file names are specified, it loads all .wav files in the directory.

    Args:
        directory_path (str): The relative path to the directory containing .wav files.
        file_names (list, optional): A list of specific .wav file names to load. Defaults to None.

    Returns:
        list: A list of numpy arrays, each containing the waveform data for a .wav file in the specified directory.
    
    Raises:
        FileNotFoundError: If the specified directory does not exist or a specified file is not found.
        ValueError: If the directory does not contain any .wav files or the file names list is empty.
    """
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    
    if file_names is None:
        wav_files = [f for f in os.listdir(directory_path) if f.endswith('.wav')]
    else:
        if not file_names:
            raise ValueError("The file names list is empty.")
        wav_files = [f for f in file_names if f.endswith('.wav')]
        for file_name in wav_files:
            if not os.path.isfile(os.path.join(directory_path, file_name)):
                raise FileNotFoundError(f"The file {file_name} does not exist in the directory {directory_path}.")
    
    if not wav_files:
        raise ValueError(f"No .wav files found in the directory {directory_path}.")
    
    waveform_list = []
    for wav_file in wav_files:
        file_path = os.path.join(directory_path, wav_file)
        waveform, _ = sf.read(file_path)
        if waveform.ndim >1:         
            print(f"converting '{wav_file}' from stereo to mono")
            waveform = waveform.mean(axis=1)
        if waveform.ndim >2:
            raise ValueError(f"mono or stereo waveform expected, array has {waveform.ndim} dimensions")
        waveform_list.append(waveform)
    
    return waveform_list