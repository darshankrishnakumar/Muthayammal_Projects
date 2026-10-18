# Project 02: network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 2 of 55 |
| **Directory** | `project_02_network_intrusion_anomaly` |
| **Backend Port** | `http://localhost:5002` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
This paper expects to address the issue of demonstrating video conduct caught in surveillance videos for the utilizations of online ordinary conduct acknowledgment and irregularity recognition. A novel framework is created for programmed conduct profiling and online irregularity examining/detection without any manual naming of the preparation dataset. The system comprises of the following key segments: A minimal and successful conduct portrayal technique is created based on discrete scene occasion discovery. The closeness between standards of conduct are estimated based on displaying each example utilizing a Dynamic Bayesian Network (DBN). Natural gathering of behaviour designs is found through a novel ghostly bunching calculation with unsupervised model choice and highlight choice on the eigenvectors of a standardized liking network. A composite generative conduct model is developed which is fit for summing up from a small preparing set to oblige varieties in inconspicuous ordinary personal conduct standards.

---

## 🏗️ System Architecture & Workflow

```
[User / Client Interface]
          │ (HTTP REST / WebSocket)
          ▼
   [FastAPI Gateway]
          │
    ┌─────┴──────────────────────┐
    ▼                            ▼
[Preprocessing Engine]     [Inference Pipeline]
• Normalization            • Deep Neural Network
• Feature Scaling          • Confidence Scoring
    │                            │
    └──────────────┬─────────────┘
                   ▼
         [Response Formatter]
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Run Backend
```bash
python source_code/backend/main.py
```
Backend API will be live at `http://localhost:5002`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5002`.
