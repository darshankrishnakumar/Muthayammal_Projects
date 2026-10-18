# PROJECT 54: AI-Based Weather Event Classification and Short-Term Prediction Using Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Bidirectional GRU Temporal Attention Sequence Nowcasting & Severe Storm Alert System.**

```
       [Multi-Sensor Meteorological Telemetry & Doppler Radar]
                                  │
                                  ▼
           [Bidirectional GRU Temporal Attention Network]
                                  │
                                  ▼
        [Short-Term Weather Event Probabilities (2-6 Hours)]
          • Heavy Rainfall (Acc 95.8%)
          • Severe Thunderstorm / Convective Cell
          • Gale Wind Gusts & Micro-bursts
                                  │
                                  ▼
          [Real-Time Early Warning Alert & Citizen Advisory]
```

## Quickstart
```bash
cd College_54
pip install -r requirements.txt
python run_system.py --port 8054
```
Dashboard at [http://localhost:8054](http://localhost:8054)
