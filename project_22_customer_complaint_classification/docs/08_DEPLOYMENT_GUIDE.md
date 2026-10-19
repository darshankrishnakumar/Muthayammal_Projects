# 08. Production Deployment & Operations Guide

## Environment Prerequisites
- **Python Version:** Python 3.10+ (Tested on Python 3.12)
- **Dependencies:** `scikit-learn`, `joblib`, `flask`, `flask-cors`, `pandas`, `numpy`
- **Network Port:** Port 5022 (Default; configurable via `PORT` environment variable)

## Installation Steps

```bash
# 1. Navigate to project root
cd project_22_customer_complaint_classification

# 2. Install requirements
pip install -r requirements.txt

# 3. (Optional) Re-train and serialize models
python3 source_code/data/train_and_save_models.py

# 4. Start Flask production server
PORT=5022 python3 source_code/backend/app.py
```

## Production Verification

```bash
# Health check
curl -s http://127.0.0.1:5022/api/health

# Classify sample ticket
curl -s -X POST http://127.0.0.1:5022/api/classify \
     -H "Content-Type: application/json" \
     -d '{"complaint": "Unauthorized charge of $450 on credit card statement."}'

# Run test suite
python3 -m unittest discover -s source_code/tests -p "test_*.py" -v
```

## Production Process Management (systemd)
```ini
[Unit]
Description=PROJECT-022 TRIAGE-AI Customer Complaint Engine
After=network.target

[Service]
User=appuser
WorkingDirectory=/opt/project_22_customer_complaint_classification
Environment="PORT=5022"
ExecStart=/usr/bin/python3 source_code/backend/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
