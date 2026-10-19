# Project 30: Production Deployment Guide

## 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Node.js 18+ (for Puppeteer automation)
- PyTorch 2.0+ (`pip install torch torchvision`)

## 2. Installation
```bash
cd project_30_iot_anomaly/source_code/backend
pip install -r requirements.txt
python3 database.py  # Initializes SQLite iot_security.db in WAL mode
```

## 3. Starting the Service
```bash
export PORT=5030
python3 app.py
```
The REST API will bind to `http://127.0.0.1:5030`.

## 4. Accessing the Frontend
Open `project_30_iot_anomaly/source_code/frontend/index.html` in any web browser or navigate directly to `http://127.0.0.1:5030/`.

## 5. Running the QA Test Suite
```bash
python3 -m unittest project_30_iot_anomaly/source_code/tests/test_api_and_system.py
```
