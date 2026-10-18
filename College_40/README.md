# PROJECT 40: AI-Based Fire and Smoke Detection Using Real-Time Video Surveillance

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Real-Time Dual-Stream Deep Learning Video Surveillance Fire & Smoke Early Warning CAD System.**

```
       [CCTV Surveillance Stream]
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  [Spatial Stream]   [Temporal Stream]
  • Chromatic Cues   • 5-20Hz Flame Flicker FFT
  • Smoke Plumes     • Plume Expansion Vector
         │                   │
         └─────────┬─────────┘
                   ▼
       [Cross-Attention Fusion]
                   │
                   ▼
       [Automated CAD Dispatch]
```

## Quickstart
```bash
cd College_40
pip install -r requirements.txt
python run_system.py --port 8040
```
Dashboard at [http://localhost:8040](http://localhost:8040)
