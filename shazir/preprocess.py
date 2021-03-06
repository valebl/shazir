# import time
import os
import librosa
import numpy as np
import librosa.display


def convert_mp3_to_wav():

    '''convert_mp3_to_wav: simple function to convert all mp3 files
    into wav files (for Windows operating system).    
    '''

    print(os.getcwd())
    os.chdir('../resources/database/mp3')
    os.system('for %i in (*.mp3) do ffmpeg -i "%i" "%~ni.wav"')
    os.chdir('../../../shazir')
    

def process_audio_file(audio_file, frame_size=2048, hop_size=512):

    '''process_audio_file: takes a .wav audio file and returns the
    values defining its spectrogram, calculated using the librosa library.

    Args:
        audio_file: audio track in .wav format
        frame_size: number of samples in the time frame - should be a
            power of two
        hop_size: number of time samples in between successive frames - should
            be a power of two
    
    Returns:
        A tuple consisting of an array of time samples [s], an array of the
        frequency samples [Hz] and a 2D array of the amplitudes [dB],
        normalized in [0,1].
    '''

    print(f'Processing track: {audio_file}')
    # start = time.time()
    audio_signal, sample_rate = librosa.load(audio_file)
    audio_stft = librosa.stft(audio_signal, n_fft=frame_size,
        hop_length=hop_size)  # Short-Time Fourier-Transform
    amp = np.abs(audio_stft)**2
    amp_log = librosa.power_to_db(amp)  # Decibel
    amp_log_norm = amp_log / amp_log.max()
    times = librosa.frames_to_time(np.arange(amp_log.shape[1]),
        sr=sample_rate, hop_length=hop_size)
    frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=frame_size)
    # end = time.time()
    # print(f'process_audio_file took {end - start} s')

    return times, frequencies, amp_log_norm
