# PROJECT 46: Automated Product Defect Detection in Manufacturing Using Vision-Based Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Industry 4.0 Feature Pyramid Network (FPN) Real-Time Visual Quality Inspection & Pneumatic Ejector System.**

```
       [High-Speed Assembly Line Camera Feed]
                         │
                         ▼
             [Feature Pyramid Network]
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
    [Defect Mask FPN]           [Defect Classifier]
    • Pixel Heatmap             • Scratch / Dent / Crack
    • Dimension & Area %        • Missing Component
           │                           │
           └─────────────┬─────────────┘
                         ▼
        [Severity Rating & Pneumatic Actuator]
```

## Quickstart
```bash
cd College_46
pip install -r requirements.txt
python run_system.py --port 8046
```
Dashboard at [http://localhost:8046](http://localhost:8046)
