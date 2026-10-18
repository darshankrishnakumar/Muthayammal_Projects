# Project 01: A Holistic Approach on Airfare Price Prediction Using LSTM Machine Learning Techniques

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 1 of 55 |
| **Directory** | `project_01_airfare_price_prediction` |
| **Backend Port** | `http://localhost:5001` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
Globalization of markets involves new strategies and price policies from professionals that contribute to global competitiveness .The pricing of tickets is frequently changed by airline companies based on a range of criteria, including their own proprietary rules and algorithms that look for the best possible price policy. Artificial Intelligence (AI) models are being used more and more for the latter task because of its various potentials in data generalisation, compactness, and quick adaptability. Artificial intelligence (AI) techniques are used to evaluate airfare price prediction and identify similarities among airline firms' pricing strategies. In this, we are using LSTM algorithm, which helps us to achieve accuracy of ~95 in this regression problem, for different international destination and airline companies. "network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection

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
Backend API will be live at `http://localhost:5001`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5001`.
