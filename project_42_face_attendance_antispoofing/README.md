# PROJECT 42: Automated Attendance Monitoring Using Face Recognition and Anti-Spoofing Techniques

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Touchless Enterprise Attendance Platform with ArcFace Embeddings and Liveness Presentation Attack Defense.**

```
       [Live Facial Scanner Feed]
                   │
                   ▼
       [Deep Biometric Backbone]
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  [ArcFace Embedder]   [Liveness Head]
  • 512-D Representation • 2D Photo Rejection
  • Cosine Similarity    • Screen Playback Guard
         │                   │
         └─────────┬─────────┘
                   ▼
     [Attendance Ledger & Alert]
```

## Quickstart
```bash
cd College_42
pip install -r requirements.txt
python run_system.py --port 8042
```
Dashboard at [http://localhost:8042](http://localhost:8042)
