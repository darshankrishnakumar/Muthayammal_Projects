# Deployment Guide: Production Microservice Setup

## 1. System Requirements
- OS: Linux (Ubuntu 22.04 LTS recommended) or macOS
- Python: 3.10+ (tested on Python 3.12)
- Memory: Minimum 2 GB RAM (Engine requires <200 MB)
- Port: 5037 (Configurable via `PORT` environment variable)

## 2. Installation
```bash
cd project_37_traffic_violation
pip install -r requirements.txt
```

## 3. Database Initialization
```bash
python3 source_code/backend/database.py
```

## 4. Launch Service
```bash
python3 source_code/backend/app.py
```
Endpoint available at `http://127.0.0.1:5037/`

## 5. Verification
```bash
python3 -m unittest discover -s source_code/tests -p "test_*.py"
```
