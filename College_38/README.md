# PROJECT 38: Pavement Crack Detection and Severity Assessment Using Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Automated Highway & Urban Road Pavement Crack Semantic Segmentation and ASTM D6433 PCI Rating System.**

```
   [Drone / Inspection Vehicle Camera]
                   │
                   ▼
       [ResUNet Pixel Segmenter]
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  [Crack Mask]       [Geometric Analyzer]
  • Pixel Heatmap    • Width (mm) & Length (cm)
  • Density Ratio    • Orientation (Long/Trans/Alligator)
         │                   │
         └─────────┬─────────┘
                   ▼
      [ASTM D6433 Severity Engine]
      • PCI Score Calculation (0-100)
      • Maintenance Work Order Dispatch
```

## Quickstart
```bash
cd College_38
pip install -r requirements.txt
python run_system.py --port 8038
```
Dashboard at [http://localhost:8038](http://localhost:8038)
