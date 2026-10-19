# Setup & Execution Guide

## 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Dependencies: `fastapi`, `uvicorn`, `torch`, `scikit-learn`, `joblib`, `pandas`, `numpy`, `pytest`, `requests`

## 2. Installation
```bash
pip install fastapi uvicorn torch scikit-learn joblib pandas numpy pytest requests
```

## 3. Launching the Backend Server
From `project_13_crime_prediction_forecasting/source_code/backend/`:
```bash
python main.py
```
Server starts on Port 5013:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:5013
```

## 4. Running the Test Suite
From `project_13_crime_prediction_forecasting/source_code/`:
```bash
pytest tests/
```
Output:
```
====================== 29 passed in 1.73s =======================
```
