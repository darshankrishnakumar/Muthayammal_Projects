# PROJECT 50: AI-Based Handwritten Document Recognition and Information Extraction Using Deep Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Enterprise Intelligent Document Processing (IDP), CRNN-CTC Handwriting Recognition & Semantic Normalization.**

```
        [Handwritten Intake Form Scan (PDF/JPG)]
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
[Document Layout Analyzer]       [Deep CRNN HTR Model]
• Form Bounding Boxes            • Convolutional Map
• Signature Zone Detection       • Bi-GRU Sequence Modeling
        │                                   │
        └─────────────────┬─────────────────┘
                          ▼
         [Semantic Entity Field Normalizer]
                          │
                          ▼
       [Structured JSON Ledger & Human-in-the-Loop Review]
```

## Quickstart
```bash
cd College_50
pip install -r requirements.txt
python run_system.py --port 8050
```
Dashboard at [http://localhost:8050](http://localhost:8050)
