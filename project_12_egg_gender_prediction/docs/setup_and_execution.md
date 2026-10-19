# Setup & Execution Instructions

## 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Virtual environment or system Python
- Supported OS: Linux, macOS, Windows

## 2. Dependencies
Install required dependencies:
```bash
pip install flask pillow numpy pytest
```

## 3. Starting the Web Application
Navigate to `project_12_egg_gender_prediction/source_code/` and run:
```bash
python app.py
```
The application initializes on Port 5012:
```
[*] Starting Egg Prediction Server on http://localhost:5012
```

## 4. Running the Test Suite
Execute all automated unit and integration tests:
```bash
pytest tests/
```
Output:
```
============================== 26 passed in 0.28s ==============================
```

## 5. Standalone CLI Batch Evaluation
Execute standalone command-line evaluation:
```bash
python test_model.py
```
