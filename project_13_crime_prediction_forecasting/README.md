# Project 13: EMPIRICAL ANALYSIS FOR CRIME PREDICTION AND FORECASTING USING MACHINE LEARNING AND DEEP LEARNING TECHNIQUES

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 13 of 55 |
| **Directory** | `project_13_crime_prediction_forecasting` |
| **Backend Port** | `http://localhost:5013` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
Crime forecasting is one of the most wanted possible forecasts, as it could lead to fewercrimes and fewer police forces to secure threatened areas. However, predicting whenand where crime will happen is challenging. Even modern predictive policing methodsdon’t provide a reasonable or accurate approximation to forecast crimes. It has a longhistory of experiments and tests to reduce and to prevent crime. Deep Learning is arelatively new machine learning topic, which achieved state-of-the-art performance inmany tasks and slowly but surely changes the machine learning area. For a few tasks,it is even better than the human himself This success leads to the questions "Is deep learning able to forecast crime as ac-curate or even better as a human?" and "How to forecast crime using deep learningtechniques?".

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
Backend API will be live at `http://localhost:5013`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5013`.
