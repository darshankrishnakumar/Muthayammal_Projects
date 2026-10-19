# Setup and Execution Guide - Child Gait Prediction System

## System Prerequisites
- **Python**: 3.9+ (Tested on Python 3.12)
- **Node.js**: v18+ (Required for Puppeteer screen-recording automation)
- **FFmpeg**: v5+ (Required for H.264 video encoding)
- **RAM**: 4 GB minimum
- **Disk Space**: ~300 MB

---

## 1. Environment Installation

Navigate to the project root directory:

```bash
cd project_06_child_gait_prediction
```

Install dependencies in a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Key Python Dependencies
- `fastapi>=0.110.0`
- `uvicorn>=0.28.0`
- `scikit-learn>=1.5.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `joblib>=1.3.0`
- `pytest>=8.0.0`

---

## 2. Model Re-Training (Zero-Leakage Pipeline)

To execute the complete participant-level zero-leakage training and tuning pipeline:

```bash
python3 source_code/ml-service/src/run_real_pipeline.py
```

This generates:
- `gait_final_model.joblib`: Tuned Random Forest (50 trees, max depth 3).
- `gait_preprocessor.joblib`: Fitted StandardScaler and LabelEncoder.
- `gait_random_forest_baseline.joblib`: Baseline comparison model.
- Performance charts in `source_code/ml-service/reports/`.

---

## 3. Running the Unified Web Application

Start the FastAPI server:

```bash
python3 source_code/backend/main.py
```

By default, the application runs on **Port 5006**:
```
 * Running on http://127.0.0.1:5006
 * Auto-seeded SQLite database: gait_database.db
```

Open `http://127.0.0.1:5006` in your browser.

---

## 4. Running the Automated Test Suite

Execute all 23 automated tests using pytest:

```bash
pytest source_code/tests/ -v
```

Expected output:
```
============================== 23 passed in 1.05s ==============================
```

---

## 5. Capturing Video Demonstrations

To reproduce the automated 3-minute video walkthrough:

```bash
node scripts/recording/record_project_06.js
```
