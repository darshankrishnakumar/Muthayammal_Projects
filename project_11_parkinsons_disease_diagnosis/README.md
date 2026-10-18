# Project 11: DEEP LEARNING BASED PARKINSON’S DISEASE DIAGNOSIS THROUGH RECURRENT NEURAL NETWORKS WITH INCEPTION NET MODELS

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 11 of 55 |
| **Directory** | `project_11_parkinsons_disease_diagnosis` |
| **Backend Port** | `http://localhost:5011` |
| **Frontend** | Standalone Interactive Portal (`source_code/frontend/index.html`) |

---

## 📄 Abstract
Long Short-Term Memory (LSTM) networks are a leading model for Computer-Aided Diagnosis (CAD) systems because they are highly regarded in deep learning (DL) and have shown promising results in medical dataset processing. In addition to Parkinson's Disease (PD), which is commonly diagnosed with Single Photon Emission Computed Tomography (SPECT) scans, their value extends to the detection of neurological disorders. However, relying entirely on visual assessment of SPECT datasets during medical tests can lead to errors due to subjective considerations. To address this issue, we propose a CAD system that utilizes pre-trained LSTM models, the Deep Learning (DL) approach, and the Bilinear Pooling method. Inception Net models and a custom LSTM architecture are incorporated into this study. These pre-trained architectures were developed using the DL approach after being trained on the Inception Net. Three Bilinear LSTM models are produced by combining these architectures with bilinear pooling techniques. These models are applied to three distinct datasets of pre-processed SPECT imaging data from PD patients and Healthy Controls (HC).

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
Backend API will be live at `http://localhost:5011`.

### 3. Launch Frontend Dashboard
Open `source_code/frontend/index.html` directly in any modern web browser or access via `http://localhost:5011`.
