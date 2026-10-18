# PROJECT 39: Real-Time Sign Language Recognition and Speech Conversion Using Deep Neural Networks

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Real-Time Landmark Spatio-Temporal Sequence Modeling, Gloss Mapping, and Natural Voice Speech Synthesis.**

```
   [Video Stream / Camera Landmarks (MediaPipe 54-D)]
                           │
                           ▼
          [Temporal Bi-LSTM + Self-Attention]
                           │
                           ▼
          [Recognized Gesture Gloss Sequence]
                           │
                           ▼
        [Natural Language Grammar Synthesizer]
                           │
                           ▼
        [Text-to-Speech (TTS) Voice Engine]
```

## Quickstart
```bash
cd College_39
pip install -r requirements.txt
python run_system.py --port 8039
```
Dashboard at [http://localhost:8039](http://localhost:8039)
