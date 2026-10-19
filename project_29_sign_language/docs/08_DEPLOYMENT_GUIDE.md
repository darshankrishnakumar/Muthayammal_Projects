# Project 29: Production Deployment Guide

## 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Node.js 18+ (for Puppeteer automation)
- PyTorch 2.0+ (`pip install torch torchvision`)

## 2. Installation
```bash
cd project_29_sign_language/source_code/backend
pip install -r requirements.txt
python3 database.py  # Initializes SQLite sign_language.db in WAL mode
```

## 3. Starting the Service
```bash
export PORT=5029
python3 app.py
```
The REST API will bind to `http://127.0.0.1:5029`.

## 4. Accessing the Frontend
Open `project_29_sign_language/source_code/frontend/index.html` in any modern web browser or navigate directly to `http://127.0.0.1:5029/`.

## 5. Running the QA Test Suite
```bash
python3 -m unittest project_29_sign_language/source_code/tests/test_api_and_system.py
```
