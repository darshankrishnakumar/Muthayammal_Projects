# VIGILANCE-AI Deployment & Operations Guide

## 1. Quickstart Run
```bash
cd project_35_driver_drowsiness
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run production REST service on Port 5035
python3 source_code/backend/app.py
```

## 2. Systemd Service Configuration
Create `/etc/systemd/system/vigilance-ai.service`:
```ini
[Unit]
Description=AI Driver Drowsiness & Fatigue Vigilance Detection System (Port 5035)
After=network.target

[Service]
Type=simple
User=automotive
WorkingDirectory=/opt/vigilance_ai/project_35_driver_drowsiness
ExecStart=/opt/vigilance_ai/.venv/bin/python3 source_code/backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## 3. Edge Containerization (Docker)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5035
CMD ["python3", "source_code/backend/app.py"]
```
