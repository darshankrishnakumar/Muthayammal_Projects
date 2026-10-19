# Deployment Guide & Operational Maintenance

## 1. Environment Requirements
- **Operating System**: macOS (Apple Silicon M-series or Intel) or Linux (Ubuntu 20.04+).
- **Python Runtime**: Python 3.10, 3.11, or 3.12.
- **Dependencies**: Flask, flask-cors, numpy, scikit-learn, joblib, pandas.

## 2. Quickstart Execution
```bash
# Navigate to project directory
cd project_21_credit_card_fraud

# Install Python dependencies
pip install -r requirements.txt

# Run automated QA test suite (31 tests)
python3 -m unittest discover -s source_code/tests -p "test_*.py" -v

# Launch the production service on Port 5021
python3 source_code/backend/app.py
```

## 3. Verification & Live Dashboard
Access the tactical FinTech dashboard by pointing any Chromium browser to:
`http://127.0.0.1:5021/`
