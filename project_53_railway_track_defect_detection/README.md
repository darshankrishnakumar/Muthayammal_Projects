# PROJECT 53: Intelligent Railway Track Defect Detection Using Computer Vision and Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **ResUNet Semantic Defect Segmentation & Geotagged Chainage Asset Maintenance System.**

```
          [Inspection Vehicle Track Optical Imagery]
                              │
                              ▼
           [ResUNet Multi-Class Defect Segmenter]
                              │
                              ▼
        [Pixel-Level Defect Masks: Cracks, Fasteners, Joints]
                              │
                              ▼
        [ASTM Severity Scoring & GPS Chainage Geotagging]
                              │
                              ▼
       [Automated Slow-Order Dispatch & Work Order Registry]
```

## Quickstart
```bash
cd College_53
pip install -r requirements.txt
python run_system.py --port 8053
```
Dashboard at [http://localhost:8053](http://localhost:8053)
