# 04. Data Pipeline & Acoustic Features

## Acoustic Feature Vector (40 Dimensions)
The feature extraction pipeline constructs a comprehensive 40-dimensional acoustic representation per speech utterance:

| Feature Subset | Dimensions | Acoustic Property Captured | Extraction Technique |
|:---------------|:----------:|:--------------------------|:--------------------|
| MFCC Means     | 13         | Vocal tract envelope & formant resonance | 25ms Hamming STFT + Mel Filterbank + DCT-II |
| MFCC Stds      | 13         | Temporal variance of cepstral coefficients | Standard deviation across time frames |
| Pitch F0 & Std | 2          | Fundamental vocal fold vibration frequency | Autocorrelation / Harmonic Product Spectrum |
| RMS Energy     | 1          | Perceived signal loudness & vocal power | $\sqrt{\frac{1}{N} \sum x[n]^2}$ |
| Spectral Centroid| 1        | Perceived brightness (spectral center of mass) | Weighted spectral frequency mean |
| Spectral Rolloff | 1        | High-frequency energy boundary (85th percentile)| Cumulative power distribution |
| Zero-Crossing  | 1          | Rate of waveform sign transitions | Noise vs. voiced distinction |
| Jitter & Shimmer| 2         | Cycle-to-cycle frequency & amplitude perturbation | Micro-tremor pitch and energy instability |
| Chroma Bands   | 4          | Harmonic pitch distribution across octaves | Folded spectral energy bands |
| Spectral Contrast| 2        | Peak-to-valley spectral dynamics | Sub-band octave contrast |
| **Total Vector**| **40**     | **Holistic Affective Representation** | **Standardized via Learned Scalers** |

## Dataset Partitioning
- **Total Corpus:** 5,000 multilingual audio feature representations across 8 languages.
- **Training Set (70%):** 3,500 samples.
- **Validation Set (15%):** 750 samples.
- **Test Set (15%):** 750 samples.\n