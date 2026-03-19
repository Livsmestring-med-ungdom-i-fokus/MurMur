import torch
import torch.nn as nn


class SimpleAutoencoder(nn.Module):
    """A tiny fully-connected autoencoder for fixed-size mel patches.

    Input shape: (batch, n_mels, seq_len)
    """
    def __init__(self, n_mels=80, latent_dim=128, seq_len=128):
        super().__init__()
        self.n_mels = n_mels
        self.seq_len = seq_len
        self.flat = n_mels * seq_len
        self.encoder = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flat, latent_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, self.flat),
            nn.Unflatten(1, (n_mels, seq_len)),
        )

    def forward(self, x):
        z = self.encoder(x)
        x_rec = self.decoder(z)
        return x_rec


class ConvAutoencoder(nn.Module):
    """A small convolutional autoencoder for mel-spectrogram patches.

    Expects input shape: (batch, 1, n_mels, seq_len)
    Works best when `n_mels` and `seq_len` are divisible by 4 (two downsamples).
    """
    def __init__(self, n_mels=80, latent_dim=256, seq_len=128):
        super().__init__()
        self.n_mels = n_mels
        self.seq_len = seq_len
        # Encoder: (B,1,n_mels,seq_len) -> downsample twice
        self.enc_conv = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
        )
        # compute spatial size after two stride-2 ops
        self.h = n_mels // 4
        self.w = seq_len // 4
        self.flat = 128 * self.h * self.w
        self.fc_enc = nn.Linear(self.flat, latent_dim)
        self.fc_dec = nn.Linear(latent_dim, self.flat)
        # Decoder: upsample back
        self.dec_conv = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=3, padding=1),
        )

    def forward(self, x):
        z = self.enc_conv(x)
        z = z.view(z.size(0), -1)
        z = self.fc_enc(z)
        z = self.fc_dec(z)
        z = z.view(-1, 128, self.h, self.w)
        x_rec = self.dec_conv(z)
        # output shape: (B,1,n_mels,seq_len)
        return x_rec.squeeze(1)


def get_model(model_type: str, n_mels=80, seq_len=128, latent=128):
    if model_type == 'conv':
        return ConvAutoencoder(n_mels=n_mels, latent_dim=latent, seq_len=seq_len)
    return SimpleAutoencoder(n_mels=n_mels, latent_dim=latent, seq_len=seq_len)
