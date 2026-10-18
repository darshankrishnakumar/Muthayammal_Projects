# PROJECT 43: AI-Based Document Forgery Detection Using Image Processing and Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Multi-Domain Spatial Error Level Analysis (ELA) and Frequency DCT Forensic Tampering Detection.**

```
       [Questioned Document Scan (PDF/JPG)]
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
  [Spatial ELA Stream]     [Frequency Noise Stream]
  • Quantization Discrepancy • DCT 2D High-Pass Filter
  • Copy-Move Boundaries     • Splicing Texture Discontinuity
         │                           │
         └─────────────┬─────────────┘
                       ▼
          [Dual-Domain Forensic Net]
                       │
                       ▼
         [Pixel Tampering Heatmap & Audit]
```

## Quickstart
```bash
cd College_43
pip install -r requirements.txt
python run_system.py --port 8043
```
Dashboard at [http://localhost:8043](http://localhost:8043)
