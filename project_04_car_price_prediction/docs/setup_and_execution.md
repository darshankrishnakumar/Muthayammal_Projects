# Setup and Execution Guide

This guide describes how to install dependencies, run the test suite, and start the AutoValuate AI microservice on Port 5004.

---

## 1. Prerequisites

- Python 3.10+ (Verified on Python 3.12.8)
- pip package manager
- macOS / Linux / Windows WSL2

---

## 2. Installation

Clone or navigate to the project directory:

```bash
cd project_04_car_price_prediction/source_code
```

Install the required Python dependencies:

```bash
pip install -r ../requirements.txt
```

Core libraries installed:
- `fastapi >= 0.100.0`
- `uvicorn >= 0.22.0`
- `scikit-learn >= 1.3.0`
- `pandas >= 2.0.0`
- `numpy >= 1.24.0`
- `joblib >= 1.3.0`
- `jinja2 >= 3.1.0`
- `pytest >= 7.4.0`
- `httpx >= 0.24.0`

---

## 3. Running Automated Tests

Execute the 18-test validation suite:

```bash
cd project_04_car_price_prediction/source_code
pytest tests/test_api_and_model.py -v
```

Expected output:
```text
============================== 18 passed in 2.51s ==============================
```

---

## 4. Starting the Web Server

Launch the FastAPI application on Port 5004:

```bash
cd project_04_car_price_prediction/source_code
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 5004
```

Access the interactive web portal at:
```
http://127.0.0.1:5004
```

Access the interactive OpenAPI Swagger documentation at:
```
http://127.0.0.1:5004/docs
```
