# Project 10: Deep fake detector using deep learning

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 10 of 55 |
| **Directory** | `project_10_deepfake_detector` |
| **Backend Port** | `http://localhost:5010` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
The Deepfake Detector using Deep Learning project aims to identify and classify manipulated digital media, specifically images and Images, generated through advanced AI techniques. Leveraging the capabilities of convolutional neural networks (CNN) and deep learning models, the system extracts subtle facial and visual features that distinguish authentic content from synthetic manipulations. The project involves preprocessing media data, training a robust neural network model, and evaluating its performance on diverse datasets to ensure reliable detection. By providing a scalable and automated approach, this project addresses the growing threat of misinformation and digital forgery, offering a practical solution for media verification, social media monitoring, and digital forensics.

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
Backend API will be live at `http://localhost:5010`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5010`.
