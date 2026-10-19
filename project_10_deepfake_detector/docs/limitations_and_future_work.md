# Limitations and Future Work: PROJECT-010

## Current Limitations
1. **Still Image Scope**: Evaluates individual facial crops rather than continuous video streams with temporal motion cues.
2. **Crop Dependency**: Requires pre-aligned frontal or semi-profile facial bounding boxes.
3. **Adversarial Post-Processing**: Aggressive JPEG re-compression (quality < 50) dampens high-frequency Fourier signals.

## Future Engineering Roadmap
1. **Temporal Video Forensics**: Incorporate 3D CNNs or Temporal Transformers to detect inter-frame flickering.
2. **Biometric Pulse Detection (rPPG)**: Extract sub-surface photoplethysmography heart rate signals from facial skin patches.
3. **Adversarial Defense Hardening**: Train with randomized adversarial perturbations to counter deepfake evasion purifiers.
