# Setup and Execution Guide: PROJECT-011

## Prerequisites
- macOS, Linux, or Windows with WSL2
- Python 3.10+ (Tested on Python 3.12.8)
- PyTorch 2.0+, Scikit-Learn, FastAPI, Uvicorn, Pandas

## Installation Steps
1. Navigate to project root:
```bash
cd project_11_parkinsons_disease_diagnosis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the FastAPI service:
```bash
python3 source_code/backend/main.py
```
Server starts on `http://127.0.0.1:5011`.

4. Access web portal:
Open browser to `http://127.0.0.1:5011`.

## Automated Test Execution
```bash
pytest source_code/tests/ -v
```
