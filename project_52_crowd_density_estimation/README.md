# PROJECT 52: AI-Based Crowd Density Estimation and Anomaly Detection for Public Safety

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Dilated Spatio-Temporal Convolutional Density Estimator (CSRNet) with Optical Flow Stampede/Surge Anomaly Detection.**

```
          [High-Density Surveillance Video Stream]
                              │
                              ▼
           [CSRNet Dilated Convolutional Extractor]
                              │
                              ▼
           [High-Resolution Density Heatmap (MAE 4.8)]
                              │
                              ▼
         [Optical Flow & Turbulence Anomaly Detector]
           • Sudden Dispersal Detection
           • Dangerous Congestion Gating
           • Stampede & Surge Intervention Alerts
                              │
                              ▼
         [Public Safety Dashboard & Real-Time Alerts]
```

## Quickstart
```bash
cd College_52
pip install -r requirements.txt
python run_system.py --port 8052
```
Dashboard at [http://localhost:8052](http://localhost:8052)
