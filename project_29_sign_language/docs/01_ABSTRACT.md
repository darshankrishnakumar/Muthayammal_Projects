# Project 29: AI-Based Sign Language Translation with Real-Time Speech and Text Generation
## 1. Abstract & Executive Summary

Over 430 million people worldwide live with disabling hearing loss. Communication between sign language users (ASL/ISL) and hearing non-signers remains a major societal barrier. Traditional translation approaches either require intrusive sensor gloves or compute-heavy 3D video convolutional networks that introduce hundreds of milliseconds of latency.

Project 29 presents a real-time, low-latency sign language translation and speech synthesis platform powered by dual deep learning models and MediaPipe 21-joint 3D hand skeletal tracking. Hand configurations are transformed into a normalized 63-dimensional coordinate tensor, reducing input data volume by 94% compared to raw video while preserving complete articulatory kinematics.

### Key Contributions
- **Dual PyTorch Deep Models**:
  1. `SignSpatialClassifier`: 4-layer Deep Residual Landmark Classifier (1.39 MB) achieving **92.89%** test accuracy across 38 ASL/ISL classes.
  2. `SignSequenceBiLSTM`: 2-layer Bidirectional LSTM with temporal self-attention (807 KB) achieving **89.39%** accuracy for dynamic gestures and gesture boundary transitions.
- **Atmospheric Landmark Dataset**: 5,700 synthesized 3D coordinate samples across 38 classes (150 samples/class) with biomechanical joint angles and perspective noise.
- **ACID Persistence Layer**: SQLite database (`sign_language.db`) running in Write-Ahead Logging (WAL) mode for non-blocking concurrent reads and audits.
- **Natural Voice Synthesis**: W3C Web Speech API integration with phonetic prompt expansion and sub-30ms audio playback latency.
- **Dedicated Port**: Bound to `http://127.0.0.1:5029/` with 31/31 passing automated tests (100% pass rate).
