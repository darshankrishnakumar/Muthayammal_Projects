# Installation, Configuration & Deployment Guide

## 1. System Requirements
- OS: macOS 11+, Linux (Ubuntu 20.04+), or Windows 10/11
- Python: Version 3.10, 3.11, or 3.12
- Node.js (Optional, for frontend development): Version 18+
- Disk Space: 250 MB
- RAM: Minimum 2 GB

## 2. Installation Steps

```bash
# 1. Navigate to project root
cd project_15_heart_disease_prediction/source_code

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the application
python app.py
```

## 3. Port Allocation
The application binds to **Port 5015** by default.
Access the web diagnostic portal at: `http://127.0.0.1:5015/`
Access API health check at: `http://127.0.0.1:5015/api/health`

## 4. Running Automated Tests
```bash
python -m pytest tests/ -v
```
