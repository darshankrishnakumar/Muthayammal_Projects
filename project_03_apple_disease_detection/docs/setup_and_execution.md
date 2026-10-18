# Setup & Execution Guide

## Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12.
- **Operating System**: macOS, Linux (Ubuntu 20.04+), or Windows 10/11 with WSL2.
- **Hardware**: Minimum 4 GB RAM, 2 GB free disk space. No GPU required (CPU inference latency $<45$ ms).

---

## 1. Local Environment Setup

### Clone Repository & Navigate
```bash
git clone https://github.com/darshankrishnakumar/Muthayammal_Projects.git
cd Muthayammal_Projects/project_03_apple_disease_detection
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
Execute the comprehensive test suite to confirm models, transforms, database, and API endpoints:
```bash
PYTHONPATH=source_code pytest source_code/tests/ -v
```
All 24 tests will pass in approximately 10 seconds.

---

## 3. Starting the Backend Server
Launch the Flask diagnostic service on port `5003`:
```bash
python3 source_code/app.py
```
You will see:
```
============================================================
 Apple Fruit Disease Prediction and Recommendation System
 URL: http://localhost:5003
 Alternative: http://127.0.0.1:5003
============================================================
 * Running on http://0.0.0.0:5003
```

---

## 4. Accessing the Web Application
Open your web browser and navigate to:
```
http://localhost:5003
```
The application will automatically load the interactive Apple Health Intelligence AI dashboard with real-time diagnosis, Grad-CAM feature maps, and the agronomic treatment guide.

---

## 5. Retraining the Models (Optional)
To retrain the MobileNetV2 leaf disease or fruit condition models:
```bash
python3 source_code/scripts/train_leaf_disease.py
python3 source_code/scripts/train_fruit_condition.py
```
