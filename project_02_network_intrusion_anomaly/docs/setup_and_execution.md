# Setup & Execution Guide

## Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12.
- **Operating System**: macOS, Linux (Ubuntu 20.04+), or Windows 10/11 with WSL2.
- **Hardware**: Minimum 4 GB RAM, 2 GB free disk space. No GPU required (CPU inference latency $<60$ ms).

---

## 1. Local Environment Setup

### Clone Repository & Navigate
```bash
git clone https://github.com/darshankrishnakumar/Muthayammal_Projects.git
cd Muthayammal_Projects/project_02_network_intrusion_anomaly
```

### Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Running Automated Verification Tests
Execute the comprehensive test suite to confirm models, database connectivity, and API endpoints:
```bash
PYTHONPATH=source_code pytest source_code/tests/ -v
```
All 19 tests will pass in under 3 seconds.

---

## 3. Starting the Backend Server
Launch the FastAPI microservice on port `5002`:
```bash
python3 -m uvicorn backend.main:app --app-dir source_code --host 127.0.0.1 --port 5002 --reload
```
You will see:
```
INFO:     Started server process [pid]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5002 (Press CTRL+C to quit)
```

---

## 4. Accessing the Web Application
Open your web browser and navigate to:
```
http://localhost:5002
```
The application will automatically load the interactive CyberShield AI Security Operations Center dashboard.

---

## 5. Retraining the Models (Optional)
To retrain the Random Forest, Extra Trees, and Isolation Forest models on the raw NSL-KDD dataset:
```bash
python3 source_code/ml/train_models.py
```
This will process `source_code/datasets/KDDTest+.txt`, regenerate `source_code/datasets/nsl_kdd_clean.csv`, and save new model weights to `source_code/models/`.
