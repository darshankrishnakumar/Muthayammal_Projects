# Installation, Configuration & Deployment Guide

## 1. System Requirements
- OS: macOS 11+, Linux (Ubuntu 20.04+), or Windows 10/11
- Python: Version 3.10, 3.11, or 3.12
- Disk Space: 500 MB (includes 146k vocabulary model and NLTK corpora)
- RAM: Minimum 2 GB

## 2. Installation Steps

```bash
# 1. Navigate to project root
cd project_14_fake_news_detection/source_code

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
python app.py
```

## 3. Port Allocation
The application binds to **Port 5014** by default.
Access the web visualizer at: `http://127.0.0.1:5014/`
Access API health check at: `http://127.0.0.1:5014/api/health`

## 4. Running Automated Tests
```bash
python -m pytest tests/ -v
```
