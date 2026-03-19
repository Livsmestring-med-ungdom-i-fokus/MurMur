import argparse
import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from music_ai_core.audio import load_audio, mel_spectrogram
from music_ai_core.model import get_model

class MelDataset(Dataset):
    def __init__(self, folder, sr=22050, n_mels=80, seq_len=128):
        self.paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.wav')]
        self.sr = sr
        self.n_mels = n_mels
        self.seq_len = seq_len

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        y, sr = load_audio(self.paths[idx], sr=self.sr)
        S = mel_spectrogram(y, sr, n_mels=self.n_mels)
        if S.shape[1] < self.seq_len:
            pad = np.zeros((self.n_mels, self.seq_len - S.shape[1]))
            S = np.concatenate([S, pad], axis=1)
        S = S[:, :self.seq_len]
        return torch.tensor(S, dtype=torch.float32)

def train(args):
    ds = MelDataset(args.data, sr=args.sr, n_mels=args.n_mels, seq_len=args.seq_len)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = get_model(args.model_type, n_mels=args.n_mels, seq_len=args.seq_len, latent=args.latent)
    model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.MSELoss()
    model.train()
    for epoch in range(args.epochs):
        total = 0.0
        for batch in dl:
            opt.zero_grad()
            # batch shape: (B, n_mels, seq_len)
            if args.model_type == 'conv':
                batch = batch.unsqueeze(1)  # (B,1,n_mels,seq_len)
            batch = batch.to(device)
            recon = model(batch)
            # recon shape for conv: (B, n_mels, seq_len) after squeeze
            loss = criterion(recon, batch.squeeze(1) if args.model_type == 'conv' else batch)
            loss.backward()
            opt.step()
            total += loss.item()
        print(f"Epoch {epoch+1}/{args.epochs} loss={total/len(dl):.4f}")
    torch.save(model.state_dict(), args.out)
    print("Saved model to", args.out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('--model_type', choices=['fc', 'conv'], default='fc', help='Model type: fc or conv')
    parser.add_argument('--out', default='model.pth')
    parser.add_argument('--sr', type=int, default=22050)
    parser.add_argument('--n_mels', type=int, default=80)
    parser.add_argument('--seq_len', type=int, default=128)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--latent', type=int, default=128)
    args = parser.parse_args()
    train(args)
