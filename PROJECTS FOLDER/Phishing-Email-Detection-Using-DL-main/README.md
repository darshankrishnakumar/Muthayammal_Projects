# Phishing Email Detection System

An email security scanner powered by Deep Learning (RCNN with Multilevel Vectors & Attention Mechanism) and structural header modeling.

## Project Structure
- `app.py`: Flask backend server and REST API endpoints.
- `phishing_engine.py`: PyTorch Deep Learning engine & classification models.
- `templates/`: HTML interface (`index.html`).
- `static/`: CSS styling and frontend JavaScript.
- `requirements.txt`: Python package dependencies.
- `run.bat`: Quick-start batch file for Windows.

## Quick Start Guide

### 1. Install Dependencies
Make sure Python 3.10+ is installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Run:
```bash
python app.py
```
*(Or double-click `run.bat` on Windows)*

### 3. Open in Browser
Visit:
```
http://localhost:5002
```
