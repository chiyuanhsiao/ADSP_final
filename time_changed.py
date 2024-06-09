import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import argparse

def main(input_file):
    # Load the audio waveform
    y, sr = librosa.load(input_file, sr=None)

    # Stretch the waveform by a factor of two using linear interpolation
    y_stretched = np.interp(
        np.arange(0, len(y), 0.5),  # New time indices (double length)
        np.arange(0, len(y)),        # Original time indices
        y                            # Original samples
    )

    # Parameters for STFT
    n_fft = 2048  # Size of FFT window
    hop_length = 512  # Hop length for STFT

    # Perform STFT on stretched waveform
    D_origin = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    D = librosa.stft(y_stretched, n_fft=n_fft, hop_length=hop_length)

    # Get the magnitude and phase
    magnitude, phase = np.abs(D), np.angle(D)

    # Shift the frequency bins by doubling their indices
    num_bins = D.shape[0]
    shift_factor = 2
    shifted_magnitude = np.zeros_like(magnitude)
    for i in range(num_bins):
        new_index = i * shift_factor
        if new_index < num_bins:
            shifted_magnitude[new_index] = magnitude[i]

    # Combine the shifted magnitude with the original phase
    D_shifted = shifted_magnitude * np.exp(1j * phase)

    # Inverse STFT to obtain the frequency-doubled sine wave
    y_doubled = librosa.istft(D_shifted, hop_length=hop_length)

    sf.write('time_changed.wav', y_doubled, sr)

    # Plot original and frequency-doubled sine waves and their spectrograms
    plt.figure(figsize=(12, 10))

    plt.subplot(4, 1, 1)
    librosa.display.waveshow(y, sr=sr)
    plt.title('Original Wave')

    plt.subplot(4, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(D_origin), ref=np.max), sr=sr, hop_length=hop_length, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Original Spectrogram')

    plt.subplot(4, 1, 3)
    librosa.display.waveshow(y_doubled, sr=sr)
    plt.title('Time-Changed Wave')

    plt.subplot(4, 1, 4)
    D_shifted_mag = np.abs(D_shifted)
    librosa.display.specshow(librosa.amplitude_to_db(D_shifted_mag, ref=np.max), sr=sr, hop_length=hop_length, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Time-Changed Spectrogram')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Path to the input audio file.')
    args = parser.parse_args()
    main(args.input_file)
