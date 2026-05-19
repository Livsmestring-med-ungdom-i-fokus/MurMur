import numpy as np
import librosa
import soundfile as sf


def load_audio(path, sr=22050):
    """Load audio file as mono."""
    y, sr = librosa.load(path, sr=sr, mono=True)
    return y, sr


def mel_spectrogram(y, sr, n_mels=80, hop_length=256, n_fft=1024):
    """Return log-scaled mel spectrogram (dB)."""
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db


def reconstruct_audio(S_mel_db, sr=22050, n_fft=1024, hop_length=256, n_mels=80, iterations=100):
    """Reconstruct waveform from mel spectrogram using Griffin-Lim algorithm.
    
    Args:
        S_mel_db: Mel spectrogram in dB scale (n_mels, time)
        sr: Sample rate
        n_fft: FFT size
        hop_length: Hop length
        n_mels: Number of mel bands
        iterations: Griffin-Lim iterations (higher = more stable but slower)
    
    Returns:
        Reconstructed audio waveform
    """
    S_mel_db = np.asarray(S_mel_db)
    if S_mel_db.ndim != 2:
        raise ValueError("S_mel_db must be a 2D mel spectrogram array (n_mels, time)")
    if iterations <= 0:
        raise ValueError("iterations must be a positive integer")

    # Convert dB mel spectrogram to power and reconstruct waveform directly.
    S_mel_power = librosa.db_to_power(S_mel_db)
    return librosa.feature.inverse.mel_to_audio(
        S_mel_power,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_iter=iterations,
    )


def save_audio(y, sr, path):
    """Save waveform to WAV file."""
    sf.write(path, y, sr)
