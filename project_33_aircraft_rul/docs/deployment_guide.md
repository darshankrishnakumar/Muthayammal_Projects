# Deployment Guide: AERO-RUL (Port 5033)

## 1. Prerequisites
- Python 3.10+
- PyTorch 2.0+
- Flask & Flask-CORS
- Node.js (for Puppeteer test automation)

## 2. Port Assignment
AERO-RUL is statically allocated to **Port 5033**:
- Application URL: `http://127.0.0.1:5033/`
- Health API: `http://127.0.0.1:5033/api/health`

## 3. Local Startup
```bash
cd project_33_aircraft_rul
python3 source_code/backend/app.py
```
Or via environment override:
```bash
PORT=5033 python3 source_code/backend/app.py
```

## 4. Database Setup & WAL Mode
The database initializes automatically on application boot at `source_code/backend/aviation_maintenance.db`.
To manually initialize or inspect WAL mode:
```bash
python3 source_code/backend/database.py
sqlite3 source_code/backend/aviation_maintenance.db "PRAGMA journal_mode;"
# Output: wal
```
