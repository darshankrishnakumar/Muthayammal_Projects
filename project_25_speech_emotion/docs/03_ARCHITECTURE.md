# 03. System Architecture & Component Design

## High-Level Architecture Diagram
```
+------------------------------------------------------------------------+
|                     CLIENT APPLICATION LAYER (PORT 5025)               |
|  - Real-Time HTML5 Spectrogram Wave Canvas (48 Frequency Bins)         |
|  - Language Selector (8 Languages) & Scenario Injection Chips          |
|  - Emotion Probability Radar Chart & 13 MFCC Bar Chart (Chart.js)      |
|  - Historical Session Ledger & Russell Circumplex Display              |
+-----------------------------------+------------------------------------+
                                    | Asynchronous JSON / REST
                                    v
+------------------------------------------------------------------------+
|                      FLASK REST APPLICATION SERVICE                    |
|  - Endpoints: /api/health, /api/recognize, /api/history, /api/stats    |
|  - Metadata & Language APIs: /api/languages, /api/model/info           |
+-------------------+--------------------------------+-------------------+
                    |                                |
                    v                                v
+-----------------------------------+  +---------------------------------+
|     DEEP SER NEURAL NETWORK       |  |  RELATIONAL SQLITE PERSISTENCE  |
|  - PyTorch DeepSERNet Architecture|  |  - Database: speech_emotion.db  |
|  - 1D-CNN + BiLSTM + Attention    |  |  - Tables: audio_sessions       |
|  - Dual Heads: 7-Class + [V, A]   |  |    emotion_benchmarks           |
|  - 40-Dimensional Standardized    |  |    language_stats, system_audit |
|    Acoustic Feature Extraction    |  +---------------------------------+
+-----------------------------------+
```

## Component Breakdown
1. **`app.py`:** Main Flask application entrypoint binding to Port 5025.
2. **`ser_model.py`:** PyTorch `MultilingualSERNet` architecture, feature extraction pipeline, and model inference engine.
3. **`database.py`:** SQLite database wrapper handling schema initialization, benchmarks seeding, CRUD operations, and audit logging.
4. **`train_and_save_ser.py`:** Standalone reproducible training script generating 5,000 samples and serializing PyTorch weights.
5. **`index.html`:** Glassmorphic dark neon single-page frontend with Chart.js visualizations.\n