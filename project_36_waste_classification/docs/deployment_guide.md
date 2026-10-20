# SORT-AI Deployment & Operations Guide

## 1. Quickstart Run
```bash
cd project_36_waste_classification
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run production REST service on Port 5036
python3 source_code/backend/app.py
```

## 2. Industrial Edge Deployment
Create `/etc/systemd/system/sort-ai.service`:
```ini
[Unit]
Description=AI Waste Classification & Autonomous Sorting System (Port 5036)
After=network.target

[Service]
Type=simple
User=mrf_operator
WorkingDirectory=/opt/sort_ai/project_36_waste_classification
ExecStart=/opt/sort_ai/.venv/bin/python3 source_code/backend/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
