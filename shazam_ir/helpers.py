import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
from matplotlib.ticker import ScalarFormatter
from skimage.feature import peak_local_max


def process_audio_file(audio_file, frame_size, hop_size):

    '''process_audio_file takes a .wav audio file and returns the
    parameters defining its spectrogram, calculated using the library librosa.

    Args:
        audio_file: audio track in .wav format
        frame_size: number of samples in the time frame - should be a
            power of two
        op_size: number of time samples in between successive frames - should
            be a power of two
    
    Returns:
        A tuple consisting of an array of time samples in s, an array of the
        frequency samples in Hz and a 2D array of the amplitude in dB.
    '''

    audio_signal, sample_rate = librosa.load(audio_file)
    audio_stft = librosa.stft(audio_signal, n_fft=frame_size,
        hop_length=hop_size)  # Short-Time Fourier-Transform
    y_audio = np.abs(audio_stft)**2
    y_log_audio = librosa.power_to_db(y_audio)  # Decibel
    times = librosa.frames_to_time(np.arange(y_log_audio.shape[1]),
        sr=sample_rate, hop_length=hop_size)
    frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=frame_size)

    return times, frequencies, y_log_audio


def make_peaks_constellation(times, frequencies, amplitudes, amp_thresh):

    '''make_peaks_constellation identifies peaks in the spectrogram. Peaks are
    time-frequency points that have higher energy content then all
    their neighbours. An minimum amplitude threshold is also considered.

    Args:
        times: array containing the time samples
        frequencies: array containing the frequency samples
        amplitudes = array containing the spectrogram amplitudes
            amplitudes.shape = (frequencies.shape, times.shape)    
        amp_thresh: minimum amplitude value for a point to be considered
            a candidate peak

    Returns:
        A tuple consisting of two arrays, respectively of the time and
        frequency coordinates of the spectogram peaks.
    '''

    peaks = peak_local_max(amplitudes, threshold_abs=amp_thresh)
    peaks_splitted = np.hsplit(peaks, 2)
    i = peaks_splitted[0]
    j = peaks_splitted[1]
    peaks_frequencies = frequencies[i]
    peaks_times = times[j]

    return peaks_times, peaks_frequencies

  
def make_combinatorial_hashes(peaks_times, peaks_frequencies, offset_time,
    offset_freq, delta_time, delta_freq):

    '''create_hashes processes the spectogram peaks into the audio
    hashes.

    Args:
        peaks_times: 
        peaks_frequencies:
        offset_time:
        offset_frequency
        delta_time:
        delta_freq:
    
    Returns:
        Returns a list containing the hases.
    '''

    def pairs_from_anchor_point(anchor_time, anchor_freq):

        start_time = anchor_time + offset_time
        start_freq = anchor_freq + offset_freq
        i = 0
        nPairs = 0
        for t in peaks_times:
            if (t > start_time and t < start_time + delta_time):
                f = peaks_frequencies[i]
                if (f > start_freq and f < start_freq + delta_freq):
                    if nPairs < fan_out:
                        hash_list.append([t[0], anchor_freq[0], f[0],
                        t[0] - anchor_time[0]])
                        nPairs += 1
                    else:
                        break
            i += 1    

    hash_list = []
    fan_out = 10
    for anchor_time, anchor_freq in zip(peaks_times, peaks_frequencies):
        pairs_from_anchor_point(anchor_time, anchor_freq)
	
    return hash_list       


def plot_spectrogram(times, frequencies, amplitudes):

    '''plot_spectrogram plots the spectrogram.

    Args:
        times: array containing the time samples
        frequencies: array containing the frequency samples
        amplitudes = array containing the spectrogram amplitudes
            amplitudes.shape = (frequencies.shape, times.shape)
    '''

    fig, ax = plt.subplots(figsize=(25,10))
    axes = plt.gca()
    out = axes.pcolormesh(times, frequencies, amplitudes, cmap='Greys')
    _ = axes.set_xlim(times.min(), times.max())
    _ = axes.set_ylim(frequencies.min(), frequencies.max())
    thresh = librosa.note_to_hz("C2")  # Defines the range (-x, x), 
                                       # within which the plot is linear
    axes.set_yscale('symlog', base=2, linthresh=thresh)
    axes.yaxis.set_major_formatter(ScalarFormatter())
    axes.yaxis.set_label_text("Frequency [Hz]")
    axes.xaxis.set_label_text("Time [s]")
    fig.colorbar(out)
    plt.title('Spectrogram')
    plt.savefig('Spectrogram.jpg')

    
def plot_peaks_constellation(frequencies, peaks_times, peaks_frequencies):

    '''plot_peaks_constellation plots the constallation map for the
        spectrogram peaks.

    Args:
        frequencies: array containing the frequency samples
        peaks_times: time values for the peaks
        peaks_frequencies: frequency values for the peaks
    '''

    fig, ax = plt.subplots(figsize=(25,10))
    axes = plt.gca()
    out = axes.scatter(peaks_times, peaks_frequencies, marker='x', s=20)
    axes.set_ylim(frequencies.min(), frequencies.max())
    thresh = librosa.note_to_hz("C2")  # Defines the range (-x, x)
                                       # within which the plot is linear
    axes.set_yscale('symlog', base=2, linthresh=thresh)
    axes.yaxis.set_major_formatter(ScalarFormatter())
    axes.yaxis.set_label_text("Frequency [Hz]")
    axes.xaxis.set_label_text("Time [s]")
    plt.title('Constellation Map')
    plt.savefig('Constellation.jpg')


def plot_matching_hash_locations(fingerprints_track, fingerprints_recording):

    '''plot_matching_hash_locations

    Args:
        fingerprints_track:
        fingerprints_recording:
    '''
    
    fig, ax = plt.subplots(figsize=(20,10))
    axes = plt.gca()

    axes.scatter(fingerprints_track, fingerprints_recording, s=100, 
        facecolors="None", edgecolor='red')  

    plt.title('Scatterplot of matching hash locations')
    plt.xlabel('Track time [s]')
    plt.ylabel('Sample time [s]')
    plt.grid()
    plt.show()


def plot_histogram_time_offsets_differences(time_offset_differences):

    '''plot_histogram_time_offsets_differences
    
    Args:
        time_offset_differences:
    '''

    fig, ax = plt.subplots(figsize=(20,10))
    plt.hist(time_offset_differences)
    plt.show()


if __name__ == '__main__':

    dir = '../resources/'
    audio_file = 'Coldplay-VioletHill.wav'
    FRAME_SIZE = 2048
    HOP_SIZE = 512
    AMP_THRES = 35

    times, frequencies, y_log_audio = process_audio_file(dir+audio_file,
        FRAME_SIZE, HOP_SIZE)
    print(f'file {audio_file} processed...')

    plot_spectrogram(times, frequencies, y_log_audio)

    peaks_times, peaks_frequencies = make_peaks_constellation(times,
        frequencies, y_log_audio, AMP_THRES)
    print(f'peaks identified...')

    plot_peaks_constellation(frequencies, peaks_times, peaks_frequencies)    