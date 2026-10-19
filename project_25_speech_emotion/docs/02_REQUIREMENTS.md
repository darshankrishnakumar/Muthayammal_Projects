# 02. System Requirements & Domain Scope

## Functional Requirements
1. **Multilingual Audio Intake & Simulation:**
   - Ingests audio speech features across 8 target languages: English, Hindi, Tamil, Spanish, French, German, Mandarin, and Japanese.
   - Accepts duration parameters, preset scenarios, and user descriptions.

2. **Digital Signal Processing & 40-Dim Feature Extraction:**
   - Computes 13 MFCC means and 13 MFCC standard deviations.
   - Extracts pitch F0 mean & std, RMS energy (dB), spectral centroid (Hz), spectral rolloff (Hz), zero-crossing rate, jitter local %, shimmer local %, 4 chroma sub-bands, and 2 spectral contrast bands.

3. **Multi-Task Deep Learning Inference:**
   - Executes PyTorch forward pass through 1D-CNN + BiLSTM + Self-Attention pooling.
   - Outputs 7-class Softmax posterior probability distribution.
   - Outputs continuous Valence and Arousal coordinates in $[-1.0, 1.0]$.

4. **Relational SQLite Persistence:**
   - Persists all analyzed audio sessions into `audio_sessions` table with full acoustic metadata.
   - Maintains `emotion_benchmarks` and `language_stats` aggregation tables.
   - Logs administrative and inference events to `system_audit`.

5. **Interactive UI Cockpit:**
   - Real-time animated 48-band spectrogram wave canvas.
   - 7-class emotion probability radar chart (Chart.js).
   - 13 MFCC spectral coefficient bar chart (Chart.js).
   - Historical audio sessions ledger.

## Non-Functional Requirements
- **Inference Latency:** $< 10$ ms per audio sample on standard CPU hardware.
- **Accuracy:** $\ge 90\%$ test classification accuracy and $\ge 0.90$ macro F1-score.
- **Port Allocation:** Exclusively bound to assigned Port 5025.\n