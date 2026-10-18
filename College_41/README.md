# PROJECT 41: AI-Based Fruit Quality Grading and Defect Detection Using Computer Vision

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **High-Throughput Agricultural Conveyor Computer Vision Quality Grading & Pneumatic Sorting System.**

```
       [High-Speed Conveyor Camera Feed]
                       │
                       ▼
            [Multi-Task ConvNet]
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
[Fruit Variety]  [Quality Grade]  [Skin Defect]
• Apple / Orange • Grade A Export • Bruise / Rot
• Mango / Banana • Grade B / C    • Area % & Severity
       │               │               │
       └───────────────┼───────────────┘
                       ▼
          [Pneumatic Sorter Actuator]
          • Bin 1: Premium Export
          • Bin 2: Domestic Standard
          • Bin 3: Reject / Composting
```

## Quickstart
```bash
cd College_41
pip install -r requirements.txt
python run_system.py --port 8041
```
Dashboard at [http://localhost:8041](http://localhost:8041)
