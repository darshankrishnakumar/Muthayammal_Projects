# 08. Deployment & Operations Guide

## Production Environment Prerequisites
- Python 3.10+
- PyTorch 2.0+
- Flask & Flask-CORS
- SQLite 3

## Quickstart Deployment
```bash
# 1. Navigate to project root
cd project_24_financial_fraud_gnn

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset and train PyTorch GCN model
python source_code/data/train_and_save_gnn.py

# 4. Launch backend server on assigned Port 5024
python source_code/backend/app.py

# 5. Access live user cockpit
open http://127.0.0.1:5024
```

## Running Verification Tests
```bash
python -m unittest discover -s source_code/tests -p "test_*.py" -v
```\n