# Setup & Execution Guide

## Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12.
- **Operating System**: macOS, Linux (Ubuntu 20.04+), or Windows 10/11 with WSL2.
- **Hardware**: Minimum 4 GB RAM, 2 GB free disk space. No GPU required (CPU inference latency $<20$ ms).

---

## 1. Local Environment Setup

### Clone Repository & Navigate
```bash
git clone https://github.com/darshankrishnakumar/Muthayammal_Projects.git
cd Muthayammal_Projects/project_01_airfare_price_prediction
```

### Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Running Automated Tests
Execute the comprehensive test suite to confirm model weights, database connectivity, and API endpoints:
```bash
PYTHONPATH=source_code pytest source_code/tests/ -v
```
All 18 tests should pass in under 3 seconds.

---

## 3. Starting the Backend Server
Launch the FastAPI microservice on port `5001`:
```bash
# From project_01_airfare_price_prediction directory:
python3 -m uvicorn backend.main:app --app-dir source_code --host 127.0.0.1 --port 5001 --reload
```
You should see:
```
INFO:     Started server process [pid]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5001 (Press CTRL+C to quit)
```

---

## 4. Accessing the Web Application
Open your web browser and navigate to:
```
http://localhost:5001
```
The application will automatically load the interactive frontend dashboard, complete with the valuation engine, model benchmarks, query history, and analytics tabs.

---

## 5. Retraining the Models (Optional)
To retrain the PyTorch BiLSTM neural network and Random Forest regressor on the raw dataset:
```bash
PYTHONPATH=source_code python3 source_code/ml/train_models.py
```
This will process `source_code/datasets/Data_Train.xlsx`, update weights in `source_code/models/`, and regenerate `source_code/models/airfare_metrics.json`.
