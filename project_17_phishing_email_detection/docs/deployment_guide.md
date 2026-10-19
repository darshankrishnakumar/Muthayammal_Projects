# Production Deployment & Operations Guide

## Requirements
- Python 3.10+
- PyTorch 2.x
- Flask 3.x
- Scikit-Learn 1.x
- SQLite3

## Installation & Launch Steps

```bash
# 1. Navigate to project root
cd project_17_phishing_email_detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start production Flask server on Port 5017
PORT=5017 python3 source_code/app.py
```

## Verification Commands
```bash
# Check service health
curl -s http://127.0.0.1:5017/health

# Run test prediction
curl -X POST http://127.0.0.1:5017/api/predict   -H "Content-Type: application/json"   -d '{"from":"alert@paypal-update.xyz","reply_to":"fraud@hack.xyz","spf_dkim":"fail","subject":"URGENT Account Suspension","email_text":"Verify password now: http://paypal-update.xyz"}'
```
