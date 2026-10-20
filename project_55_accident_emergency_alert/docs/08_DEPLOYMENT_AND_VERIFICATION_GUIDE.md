# 08 — Deployment & Verification Guide

## Prerequisites
- macOS or Linux with Python 3.10+
- PyTorch 2.0+ (with MPS / CUDA acceleration)
- Node.js 18+ (for Puppeteer and UI automation)
- FFmpeg (for video walkthrough transcoding)

## Installation & Setup
```bash
# 1. Clone repository and navigate to source directory
cd project_55_accident_emergency_alert/source_code

# 2. Install dependencies
pip install -r ../requirements.txt

# 3. Generate 6,000-record dataset and train dual PyTorch models
python backend/train_accident_models.py

# 4. Execute 31-test QA verification suite
pytest tests/test_api_and_system.py -v

# 5. Launch microservice on Port 5055
python run_system.py --port 5055
```

## Verifying Endpoints
```bash
# Health check
curl -s http://127.0.0.1:5055/api/health/

# Preset demonstration scenarios
curl -s http://127.0.0.1:5055/api/incidents/presets

# Audit ledger integrity
curl -s http://127.0.0.1:5055/api/incidents/audit-ledger?limit=5
```
