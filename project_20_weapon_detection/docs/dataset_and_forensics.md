# Dataset Engineering & Computer Vision Forensics

## 1. Dataset Composition
The model was fine-tuned on a composite curated dataset of 14,850 annotated security and surveillance frames:
- 60% Real-world CCTV and security checkpoint footage depicting holstered and drawn firearms.
- 25% High-resolution knife and bladed weapon interdiction scenarios.
- 15% Synthetic security training imagery depicting suspicious unattended packages and airport baggage scans.

### Data Augmentation Pipeline
- Random horizontal flips ($p = 0.5$)
- Mosaic augmentation ($4 \times 4$ frame recombination, $p = 0.8$)
- HSV color jittering (Hue: $\pm 0.015$, Saturation: $\pm 0.7$, Value: $\pm 0.4$)
- Random bounding-box affine scaling (0.8x to 1.2x) and perspective transforms.

## 2. Algorithmic Image Forensics Layer
In parallel with neural inference, VIGIL-8 extracts computer vision metrics on every ingested frame:
- **Sharpness Telemetry**: Calculated via the variance of the 2D discrete Laplacian:
  $$\text{Sharpness} = \text{Var}(\nabla^2 I_{gray})$$
  Scores below 45.0 trigger blur warnings to security operators.
- **Contrast & Brightness**: Mean and standard deviation of luminance channel $Y$:
  $$\text{Brightness} = \mu(I_{gray}), \quad \text{Contrast} = \sigma(I_{gray})$$
- **Canny Edge Density**:
  $$\text{Density}_{\%} = \frac{\sum (\text{Canny}(I) > 0)}{W \times H} \times 100$$
- **Morphological Aspect Ratio Heuristics**: Secondary verification for weapon-like geometric profiles (long firearms $> 2.2$, combat knives $1.5 - 3.5$, handguns $0.7 - 0.95$).
