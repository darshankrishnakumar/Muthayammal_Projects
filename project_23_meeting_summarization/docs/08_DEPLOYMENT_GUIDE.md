# 08. Production Deployment & Operations Guide

## Environment Prerequisites
- **Python Version:** Python 3.10+ (Tested on Python 3.12)
- **Dependencies:** `scikit-learn`, `joblib`, `flask`, `flask-cors`, `pandas`, `numpy`
- **Port:** Port 5023 (`http://127.0.0.1:5023`)

## Quickstart

```bash
# 1. Navigate to directory
cd project_23_meeting_summarization

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Re-train and serialize models
python3 source_code/data/train_and_save_models.py

# 4. Start Flask production server
PORT=5023 python3 source_code/backend/app.py
```

## Production Verification

```bash
# Health check
curl -s http://127.0.0.1:5023/api/health

# Run test suite
python3 -m unittest discover -s source_code/tests -p "test_*.py" -v
```
