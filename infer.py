import argparse
import numpy as np
import torch
from music_ai_core.audio import load_audio, mel_spectrogram, reconstruct_audio, save_audio
from music_ai_core.model import get_model


def infer(args):
    """Load audio, extract mel spectrogram, run through model, save output."""
    y, sr = load_audio(args.input, sr=args.sr)
    S = mel_spectrogram(y, sr, n_mels=args.n_mels)
    
    # Pad or crop to seq_len
    if S.shape[1] < args.seq_len:
        pad = np.zeros((args.n_mels, args.seq_len - S.shape[1]))
        S = np.concatenate([S, pad], axis=1)
    S = S[:, :args.seq_len]
    
    # Load model and run inference
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = get_model(args.model_type, n_mels=args.n_mels, seq_len=args.seq_len, latent=args.latent)
    model.load_state_dict(torch.load(args.model, map_location=device))
    model.to(device)
    model.eval()

    with torch.no_grad():
        x = torch.tensor(S, dtype=torch.float32).unsqueeze(0)  # (1, n_mels, seq_len)
        if args.model_type == 'conv':
            x = x.unsqueeze(1)  # (1,1,n_mels,seq_len)
        x = x.to(device)
        x_rec = model(x)
        if args.model_type == 'conv':
            x_rec = x_rec.squeeze(0).cpu().numpy()
        else:
            x_rec = x_rec.squeeze(0).cpu().numpy()
    
    np.save(args.output, x_rec)
    print(f"Saved reconstructed mel spectrogram to {args.output}")
    
    # Optionally reconstruct waveform using Griffin-Lim
    if args.save_wav:
        wav_output = args.output.replace('.npy', '.wav')
        y_rec = reconstruct_audio(x_rec, sr=sr, n_fft=args.n_fft, hop_length=args.hop_length, 
                                  n_mels=args.n_mels, iterations=args.gl_iter)
        save_audio(y_rec, sr, wav_output)
        print(f"Saved reconstructed audio to {wav_output}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input WAV file')
    parser.add_argument('--model', required=True, help='Path to trained model')
    parser.add_argument('--output', default='reconstructed.npy')
    parser.add_argument('--model_type', choices=['fc', 'conv'], default='fc')
    parser.add_argument('--save_wav', action='store_true', help='Reconstruct and save waveform using Griffin-Lim')
    parser.add_argument('--sr', type=int, default=22050)
    parser.add_argument('--n_mels', type=int, default=80)
    parser.add_argument('--seq_len', type=int, default=128)
    parser.add_argument('--latent', type=int, default=128)
    parser.add_argument('--n_fft', type=int, default=1024, help='FFT size for Griffin-Lim')
    parser.add_argument('--hop_length', type=int, default=256, help='Hop length for Griffin-Lim')
    parser.add_argument('--gl_iter', type=int, default=100, help='Griffin-Lim iterations')
    args = parser.parse_args()
    infer(args)
