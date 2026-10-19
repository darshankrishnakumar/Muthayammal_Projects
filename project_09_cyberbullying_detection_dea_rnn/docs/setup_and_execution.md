# Setup and Execution Guide: PROJECT-009

## Prerequisites
- macOS, Linux, or Windows with WSL2
- Python 3.10+ (Tested on Python 3.12.8)
- Google Chrome (Optional, for running Puppeteer automation scripts)

## Installation Steps
1. Navigate to project root:
```bash
cd project_09_cyberbullying_detection_dea_rnn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI microservice:
```bash
python3 source_code/backend/main.py
```
Server starts on `http://127.0.0.1:5009`.

4. Access the web interface:
Open browser to `http://127.0.0.1:5009`.

## Running Automated Tests
```bash
pytest source_code/tests/ -v
```
