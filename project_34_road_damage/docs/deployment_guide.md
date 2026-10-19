# Deployment Guide: ROAD-AI (Port 5034)

## 1. Prerequisites
- Python 3.10+
- PyTorch 2.0+
- Flask & Flask-CORS
- Node.js (for Puppeteer automation)

## 2. Port Allocation
ROAD-AI is statically bound to **Port 5034**:
- Application URL: `http://127.0.0.1:5034/`
- Health API: `http://127.0.0.1:5034/api/health`

## 3. Local Startup
```bash
cd project_34_road_damage
python3 source_code/backend/app.py
```
Or via environment variable:
```bash
PORT=5034 python3 source_code/backend/app.py
```

## 4. SQLite Database Initialization & WAL Mode
The database initializes automatically on boot at `source_code/backend/road_damage.db`.
To inspect WAL mode:
```bash
sqlite3 source_code/backend/road_damage.db "PRAGMA journal_mode;"
# Output: wal
```
