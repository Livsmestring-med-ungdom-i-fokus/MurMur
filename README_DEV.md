Music AI Core — Prototype

Overview
-
This repository contains a minimal prototype for a Music AI core: audio I/O, mel feature extraction, a tiny PyTorch autoencoder, and simple training/inference scripts.

Quick start
-
1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Train on a folder of WAV files:

```bash
python train.py /path/to/wav_folder --out model.pth --epochs 5
```

3. Run inference (saves reconstructed mel spectrogram as a .npy):

```bash
python infer.py input.wav --model model.pth --output reconstructed.npy
```

4. Reconstruct waveform using Griffin-Lim (convolutional model):

```bash
python infer.py input.wav --model model.pth --output reconstructed --model_type conv --save_wav
```

This saves:
- `reconstructed.npy` — Mel spectrogram from the autoencoder
- `reconstructed.wav` — Reconstructed waveform via Griffin-Lim phase estimation

Customize Griffin-Lim:
```bash
python infer.py input.wav --model model.pth --save_wav --gl_iter 200
```

Files
-
- `music_ai_core/audio.py`: audio loading, mel extraction, Griffin-Lim reconstruction
- `music_ai_core/model.py`: fully-connected and convolutional autoencoders
- `train.py`: training script with model selection
- `infer.py`: inference with optional waveform reconstruction
