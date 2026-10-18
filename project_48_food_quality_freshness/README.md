# PROJECT 48: AI-Based Food Quality and Freshness Detection Using Computer Vision

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Multi-Cue Spatio-Spectral Computer Vision Platform for Continuous Freshness Scoring & Shelf-Life Regression.**

```
       [Food Quality Camera Ingestion]
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[Color LAB Shift Stream]   [GLCM Texture Entropy]
• Oxidation & Browning     • Structural Collapse
• Discoloration Patches    • Bacterial Surface Film
       │                           │
       └─────────────┬─────────────┘
                     ▼
       [Spatio-Spectral CNN Engine]
                     │
                     ▼
    [Freshness Score (0-100) & Shelf-Life Hours]
```

## Quickstart
```bash
cd College_48
pip install -r requirements.txt
python run_system.py --port 8048
```
Dashboard at [http://localhost:8048](http://localhost:8048)
