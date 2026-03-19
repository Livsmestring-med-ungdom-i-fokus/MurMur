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
    # Convert dB to power
    S = librosa.db_to_power(S_mel_db)
    
    # Convert mel scale back to linear magnitude spectrogram
    S = librosa.feature.inverse.mel_to_audio(S, sr=sr, n_fft=n_fft, hop_length=hop_length)
    
    # Griffin-Lim algorithm to estimate phase
    y = librosa.griffinlim(S, n_iter=iterations, hop_length=hop_length)
    
    return y

def save_audio(y, sr, path):
    """Save waveform to WAV file."""
    sf.write(path, y, sr)
