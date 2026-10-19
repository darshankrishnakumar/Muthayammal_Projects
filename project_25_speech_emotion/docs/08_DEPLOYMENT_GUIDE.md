# 08. Deployment & Operations Guide

## Prerequisites
- Python 3.10+
- PyTorch 2.0+
- Flask & Flask-CORS
- SQLite 3

## Quickstart Deployment
```bash
# 1. Navigate to project root
cd project_25_speech_emotion

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset and train PyTorch SER model
python source_code/data/train_and_save_ser.py

# 4. Launch backend server on assigned Port 5025
python source_code/backend/app.py

# 5. Access live user cockpit
open http://127.0.0.1:5025
```

## Running Verification Tests
```bash
python -m unittest discover -s source_code/tests -p "test_*.py" -v
```\n