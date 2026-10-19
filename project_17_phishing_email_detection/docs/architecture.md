# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

PROJECT-017 is an enterprise-grade deep learning cybersecurity platform designed to detect structural and semantic email phishing attacks. It combines an 8-dimensional structural header integrity analyzer, sub-word character 1D convolutions, word embeddings, bidirectional recurrent context modeling (BiLSTM), and a query-key Attention Mechanism.

```
+-----------------------------------------------------------------------------------+
|                        SECURITY WEB DASHBOARD (PORT 5017)                         |
|     Dark Glassmorphism UI + Dynamic Risk Gauge + XAI Attention Heatmap + Telemetry |
+-----------------------------------------------------------------------------------+
                                         |  JSON REST API
                                         v
+-----------------------------------------------------------------------------------+
|                        PYTHON FLASK BACKEND ENGINE (PORT 5017)                     |
|         /api/predict | /api/history | /api/stats | /api/benchmark | /api/samples  |
+-----------------------------------------------------------------------------------+
          |                                                 |
          v                                                 v
+-----------------------------------------+       +---------------------------------+
|      PYTORCH MULTILEVEL RCNN ENGINE     |       |        RELATIONAL SQLITE DB     |
|                                         |       |                                 |
|  - 8-Dim Structural Header Vector       |       |  phishing_scans.db              |
|  - Sub-Word Character 1D-CNN (32-d)     |       |  - email_scans (scans log)      |
|  - Word Embedding (100-d) + BiLSTM      |       |  - ACID Transactional Logging   |
|  - RCNN Context Fusion [c_l, w_i, c_r]  |       |  - Pre-Seeded Benchmark History |
|  - Softmax Attention Energy (alpha_t)   |       |  - Aggregate Statistics Index   |
|  - 9-Model Consensus Ensemble Engine    |       +---------------------------------+
+-----------------------------------------+
```

## 2. Key Modules

### 2.1 Web Presentation Layer
- **Port Allocation**: Port 5017 (`http://127.0.0.1:5017`).
- **Templates & Static Assets**: HTML5 Jinja2 template (`templates/index.html`), custom responsive CSS (`static/css/style.css`), modular vanilla JavaScript (`static/js/app.js`).
- **Features**: 4 interactive tabs (Live Scanner, Benchmarks, History, Architecture), real-time risk gauges, preset quick selectors, XAI token attention highlighting, and 9-model consensus voting cards.

### 2.2 Deep Learning Engine (`phishing_engine.py`)
- **PyTorch RCNN Attention Model**: Combines character-level convolutions for typosquatting defense, word embeddings, and bidirectional LSTM recurrence.
- **Structural Header Feature Extractor**: Encodes envelope mismatches, SPF/DKIM verification results, urgent subject markers, free webmail impersonation, and punycode.
- **Multi-Model Consensus**: Runs 9 models in parallel (RCNN Attention, BiLSTM, LSTM, GRU, SGD, MLP, Random Forest, Naive Bayes, Logistic Regression).

### 2.3 Relational Persistence Layer
- **SQLite Engine**: `phishing_scans.db`.
- **Primary Table**: `email_scans` storing full forensic scan records, probability distributions, threat classifications, consensus vote tallies, and latency telemetry.
