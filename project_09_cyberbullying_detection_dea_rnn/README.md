# Project 09: DEA-RNN: A Combined Deep Learning Method for Cyberbullying Detection on Twitter

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 9 of 55 |
| **Directory** | `project_09_cyberbullying_detection_dea_rnn` |
| **Backend Port** | `http://localhost:5009` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
Cyberbullying is an important issue for our society and has a major negative effect on the victims that can be highly damaging due to the frequency and high propagation provided by Information Technologies. Therefore, the early detection of cyberbullying in social networks becomes crucial to mitigate the impact on the victims. In this article, we aim to explore different approaches that take into account the time in the detection of cyberbullying in social networks. We follow a supervised learning method with two different specific early detection models, named threshold and dual. The former follows a more simple approach, while the latter requires two machine learning models. To the best of our knowledge, this is the first attempt to investigate the early detection of cyberbullying. We propose two groups of features and two early detection methods, specifically designed for this problem. We conduct an extensive evaluation using a real world dataset, following a time-aware evaluation that penalizes late detections. Our results show how we can improve baseline detection models. Published by Elsevier B.V. This is an open access article under the CC BY-NC-ND license.

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
Backend API will be live at `http://localhost:5009`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5009`.
