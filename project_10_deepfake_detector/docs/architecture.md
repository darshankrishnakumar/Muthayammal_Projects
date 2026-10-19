# System Architecture: MesoInception-4 Deepfake Detection Laboratory

## 1. High-Level Architectural Pipeline
PROJECT-010 implements an advanced multi-modal computer vision forensics suite tailored for real-time facial manipulation and synthesis detection. The architecture pairs deep convolutional neural networks with 2D frequency domain analysis and boundary gradient filtering.

```
+-----------------------------------------------------------------------------------+
|                            FACIAL IMAGE INGESTION                                 |
|            (Authentic Portraits, FaceSwap, StyleGAN2/3, Latent Diffusion)          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        PREPROCESSING & STANDARDIZATION                            |
|  - Dimension Normalization: 256x256 RGB Tensor                                    |
|  - Zero-Mean Unit-Variance Scaling: (img - 0.5) / 0.5                             |
|  - Spatial Grayscale Conversion for Frequency & Gradient Analysis                 |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     MESOINCEPTION-4 DEEP CONVOLUTIONAL NETWORK                    |
|  - MesoInception Block 1: 1x1, 3x3, and 3x3 Dilated Convolutions (9 channels)     |
|  - MesoInception Block 2: Multi-Scale Inception Feature Aggregation (10 channels) |
|  - Spatial Conv Blocks 3 & 4: 5x5 Convolutions with BatchNorm & LeakyReLU         |
|  - Dense Classification Head: Linear(1024, 32) -> Dropout(0.5) -> Linear(32, 2)   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     MULTI-MODAL FORENSIC SIGNAL EXTRACTOR                         |
|  1. 2D FFT Frequency Analysis: Azimuthal Radial High-Frequency Energy Ratio       |
|  2. Morphological Boundary Seam: Sobel Gradient Discontinuity around Facial Mask  |
|  3. Chromaticity Variance: HSV Color Saturation Variance                          |
|  4. Sharpness Metric: Laplacian Variance Differential                             |
|  5. Facial Symmetry: Bilateral Eye/Iris Asymmetry Metric                         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     ENSEMBLE DECISION & GOVERNANCE ENGINE                         |
|  - Voting Classifier: MesoInception-4 + Gradient Boosting + Extra Trees           |
|  - Calibrated Confidence Score (0.00 - 1.00)                                      |
|  - Tri-Tier Moderation Directive:                                                 |
|    * APPROVED AUTHENTIC BIOMETRIC (Real >= 0.85)                                  |
|    * FLAGGED SUSPICIOUS MANIPULATION (0.50 <= Fake < 0.80)                        |
|    * CRITICAL SYNTHETIC FRAUD - QUARANTINED (Fake >= 0.80)                         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    FASTAPI REST MICROSERVICE & PERSISTENCE (PORT 5010)            |
|  - Endpoints: /health, /api/stats, /api/metrics, /api/history, /api/analyze       |
|  - Relational Database: SQLite3 (deepfake_detector.db - forensic_scans table)     |
|  - Web UI: Real-Time Preview, Diagnostic Meters, Audit Ledger Table               |
+-----------------------------------------------------------------------------------+
```

## 2. Key Technology Stack
- **Framework**: PyTorch 2.14 / Torch MPS
- **Computer Vision**: OpenCV (cv2), Pillow (PIL), NumPy
- **Backend**: FastAPI 0.115+ / Uvicorn (Port 5010)
- **Database**: SQLite3 (`source_code/data/deepfake_detector.db`)
- **Frontend**: Responsive HTML5, CSS3 Custom Properties, JavaScript
