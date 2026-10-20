# Production Deployment Guide: PROJECT-053

## 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Apple Silicon (MPS) or NVIDIA GPU (CUDA 11.8+)
- Node.js 18+ (for Puppeteer screenshot & video pipelines)
- FFmpeg 5.0+

## 2. Local Installation & Run
```bash
cd project_53_railway_track_defect_detection/source_code
pip install -r ../requirements.txt
python run_system.py --port 5053
```

## 3. Verification
Verify gateway operational status:
```bash
curl http://127.0.0.1:5053/api/health/
```

Run test suite:
```bash
pytest tests/test_api_and_system.py -v
```

## 4. Operational Maintenance
- **SQLite WAL Checkpointing**:
```bash
sqlite3 data/rail_defects.db "PRAGMA wal_checkpoint(TRUNCATE);"
```
