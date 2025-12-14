# Applied Mathematics 4: Fourier Analysis

## Overview
Implementation of Fourier transforms, signal processing techniques, and spectral analysis methods for analyzing periodic and non-periodic signals.

## Features
- **Discrete Fourier Transform (DFT)** and FFT implementation
- **Signal filtering**: Low-pass, high-pass, band-pass filters
- **Spectral analysis**: Power spectral density, spectrogram
- **Window functions**: Hamming, Hanning, Blackman
- **2D Fourier transforms** for image processing
- **Wavelet transforms**: Continuous and discrete

## Mathematical Topics
- Fourier series
- Fourier transforms
- Discrete-time signals
- Sampling theorem
- Convolution theorem
- Frequency domain analysis

## Key Equations
- `X(k) = Σ x(n)e^(-i2πkn/N)` (DFT)
- `f_s ≥ 2f_max` (Nyquist criterion)
- `x(t) * h(t) ↔ X(f)·H(f)` (Convolution theorem)

## Installation
```bash
pip install -r requirements.txt
```

## License
MIT License
