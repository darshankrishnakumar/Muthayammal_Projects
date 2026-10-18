# Medical Sensor-Based Disease Prediction and Recommendation System Using CNN

A full-stack medical health monitoring and 1D CNN-assisted arrhythmia classification system.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────┐
                      │    React + Vite Frontend (Port 8080) │
                      │   TanStack Router, Recharts, Tailwind│
                      └──────────────────┬───────────────────┘
                                         │ HTTP REST / Uploads
                                         ▼
                      ┌──────────────────────────────────────┐
                      │    Node.js Express Backend (Port 5000│
                      │    ES Modules, Zod, Helmet, Multer   │
                      └──────────┬──────────────────┬────────┘
                                 │                  │
                ┌────────────────┴────────┐         │ Local HTTP Probing
                ▼                         ▼         ▼
    ┌───────────────────────┐  ┌───────────────────────┐
    │ SQLite Database (WAL) │  │ Stored ECG Recordings │
    │ 6 Relational Tables   │  │ Non-Public Server Dir │
    └───────────────────────┘  └───────────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │ Python 1D CNN Model (ml-model/.venv) │
                      │ TensorFlow, SciPy, NumPy, WFDB       │
                      └──────────────────────────────────────┘
```

---

## Project Structure

* **[`pixel-perfect-pixels/`](./pixel-perfect-pixels/)**: Frontend web dashboard built with React 19, TanStack Router, Recharts, Lucide Icons, and Tailwind CSS.
* **[`backend/`](./backend/)**: Modular JavaScript backend built with Node.js, Express.js, and SQLite (`better-sqlite3`). Provides biometric management, ECG uploads, recommendation guidelines, and prediction history.
* **[`ml-model/`](./ml-model/)**: Python machine learning environment configured with TensorFlow, SciPy, Pandas, WFDB, and Scikit-Learn for 1D CNN arrhythmia classification using the MIT-BIH Arrhythmia Database.

---

## Quick Start Guide

### 1. Backend Setup & Run

```bash
cd backend
npm install
npm start
# Backend runs on http://localhost:5000
```

To run the backend test suite:
```bash
npm test
# 41 automated tests verifying biometrics, ECG storage, SQLite, and safety invariants
```

### 2. Frontend Setup & Run

```bash
cd pixel-perfect-pixels
npm install
npm run dev
# Frontend runs on http://localhost:8080
```

### 3. Machine Learning Environment

```powershell
cd ml-model
# Activate the Python virtual environment
.\.venv\Scripts\Activate.ps1

# Run the environment and forward-pass verification test
python verify_env.py
```

---

## Medical AI Safety Invariants

1. **No Fabricated Predictions**: The system strictly never generates synthetic disease diagnoses or fake confidence scores.
2. **Explicit 503 Guard**: While the trained CNN inference service is being integrated, prediction endpoints return an explicit `503 Service Unavailable` (`MODEL_NOT_CONNECTED`).
3. **Plausibility & Data Quality**: Biometric inputs outside physiological plausibility are rejected at the API and database levels.
4. **Educational Guidance**: Recommendations are designated as illustrative health guidelines and clearly state they do not replace a healthcare professional.
