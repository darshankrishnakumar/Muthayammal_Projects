# Project 29: Data Pipeline Specification

## 1. Landmark Generation & Augmentation
- Input coordinates: 21 landmarks × 3 dimensions ($x, y, z$).
- Biomechanical constraint rules:
  - Finger curl factors $\in [0.0, 1.0]$.
  - Thumb opposition angle $\in [-0.65, 0.55]$ radians.
  - Inter-joint bone link lengths parameterized across 4 joints per finger.
- Gaussian noise injection: $\sigma = 0.008$ per coordinate to simulate camera sensor jitter.
- Volume: 5,700 samples (150 per class × 38 classes).

## 2. Preprocessing & Normalization
- Coordinate standardization:
  $$x_{\text{norm}} = \frac{x - \mu_x}{\sigma_x + 10^{-6}}$$
- Stored scalers: `source_code/backend/landmark_scalers.json` containing 63 mean and 63 std values.
- Train/Test Split: 80% training (4,560 samples), 20% test (1,140 samples) with stratified class distribution.
