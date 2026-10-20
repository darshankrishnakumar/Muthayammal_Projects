# Production Deployment Guide: PROJECT-054

## 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Apple Silicon (MPS) or NVIDIA GPU (CUDA 11.8+)
- Node.js 18+ (for Puppeteer screenshot & video pipelines)
- FFmpeg 5.0+

## 2. Local Installation & Run
```bash
cd project_54_weather_event_prediction/source_code
pip install -r ../requirements.txt
python run_system.py --port 5054
```

## 3. Verification
Verify gateway operational status:
```bash
curl http://127.0.0.1:5054/api/health/
```

Run test suite:
```bash
pytest tests/test_api_and_system.py -v
```

## 4. Operational Maintenance
- **SQLite WAL Checkpointing**:
```bash
sqlite3 data/weather_nowcast.db "PRAGMA wal_checkpoint(TRUNCATE);"
```
