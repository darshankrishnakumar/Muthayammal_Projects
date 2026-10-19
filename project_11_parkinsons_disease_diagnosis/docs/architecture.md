# System Architecture: Inception-RNN Parkinson's Disease Diagnostics

## 1. High-Level Architectural Pipeline
PROJECT-011 implements a clinical telemonitoring and diagnostic suite designed to evaluate vocal dysphonia and laryngeal motor dysfunction for Parkinson's Disease screening. The architecture combines 1D multi-scale Inception temporal convolutions with Bidirectional LSTM sequential memory and multi-task prediction heads.

```
+-----------------------------------------------------------------------------------+
|                        ACOUSTIC TELEMONITORING STREAM                             |
|          (Patient Vocal Sustained Phonation: Fo, Jitter, Shimmer, HNR, PPE)       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        PREPROCESSING & STANDARDIZATION                            |
|  - Feature Vector Extraction: 12 Clinical Acoustic Biomarkers                     |
|  - Zero-Mean Unit-Variance Normalization: (X - mu) / sigma                        |
|  - Sequence Formatting: 1D Temporal Input Tensor                                  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     1D INCEPTION MULTI-SCALE TEMPORAL BLOCK                       |
|  - Branch 1: Pointwise 1x1 Conv (Feature cross-correlation)                       |
|  - Branch 2: 1x1 -> 3x3 Conv (Micro-flutter & glottal cycle jitter)               |
|  - Branch 3: 1x1 -> 5x5 Conv (Long-range pitch glide & laryngeal fatigue)         |
|  - Branch 4: MaxPool1d -> 1x1 Conv (Dominant harmonic energy preservation)       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    2-LAYER BIDIRECTIONAL LSTM SEQUENTIAL MEMORY                   |
|  - Forward & Backward Hidden Representations (64-dim bidirectional state)         |
|  - Internal Gating: Input, Forget, Cell, Output Gates (Zero Gradient Decay)       |
|  - Global Sequence Average Pooling -> 64-dimensional Patient State Vector        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         MULTI-TASK PREDICTION HEADS                               |
|  1. Diagnostic Classification Head: Linear(64, 32) -> Dropout(0.3) -> Linear(32, 2)|
|     -> Softmax: HEALTHY_CONTROL vs PARKINSONS_DIAGNOSED                           |
|  2. Motor UPDRS Regression Head: Linear(64, 16) -> Linear(16, 1)                  |
|     -> Estimated UPDRS Motor Score (0 - 60) -> Hoehn & Yahr Staging               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                 FASTAPI REST MICROSERVICE & PERSISTENCE (PORT 5011)               |
|  - Endpoints: /health, /api/stats, /api/metrics, /api/history, /api/diagnose      |
|  - Relational Database: SQLite3 (parkinsons_diagnosis.db)                         |
|  - Web UI: Presets, Staging Meters, Diagnostic Recommendation Banners             |
+-----------------------------------------------------------------------------------+
```

## 2. Key Technology Stack
- **Framework**: PyTorch 2.14 / Torch MPS
- **Machine Learning**: Scikit-Learn (Random Forest, Extra Trees Ensemble)
- **Backend**: FastAPI 0.115+ / Uvicorn (Port 5011)
- **Database**: SQLite3 (`source_code/data/parkinsons_diagnosis.db`)
- **Frontend**: Responsive HTML5, CSS3 Custom Properties, JavaScript
