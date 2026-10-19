# Dataset and Model Details: PROJECT-010

## 1. Curated Facial Forensics Corpus (1,000 Records)
The experimental corpus contains 1,000 balanced facial samples reflecting leading deepfake techniques:

| Category | Samples | Description |
|:---|:---:|:---|
| **Authentic Human Faces** | 500 | Genuine photographic portraits with natural sensor noise and continuous spectral fall-off. |
| **FaceSwap Manipulations** | 170 | Donor facial masks spliced onto host heads with blending contour discontinuities. |
| **StyleGAN2/3 Syntheses** | 165 | Fully synthetic AI generated faces displaying periodic checkerboard high-frequency spectral grids. |
| **Diffusion Inpainting** | 165 | Latent diffusion manipulations with localized saturation anomalies and subtle iris/pupil asymmetry. |

## 2. MesoInception-4 Model Architecture
- **Inception Kernel Sizes**: 1x1, 3x3, and 3x3 dilated convolutions
- **Convolutional Layers**: 4 blocks (2 Inception blocks, 2 standard Conv blocks)
- **Activation Functions**: LeakyReLU(0.1) across all feature extraction stages
- **Regularization**: Spatial BatchNorm2d, Dropout (0.5) on dense head
- **Input Dimensions**: 3 x 256 x 256 RGB image tensor
- **Trainable Parameters**: ~28,400 parameters (Ultra-lightweight and computationally fast)

## 3. Evaluation Benchmarks
- **Accuracy**: 99.5%
- **Macro F1-Score**: 0.995
- **ROC-AUC**: 0.999
- **Average Inference Latency**: 21.4 ms per image
