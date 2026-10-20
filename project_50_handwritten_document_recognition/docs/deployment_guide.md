# Production Deployment Guide: PROJECT-050

## 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Apple Silicon (MPS) or NVIDIA GPU (CUDA 11.8+)
- Node.js 18+ (for Puppeteer screenshot & video pipelines)
- FFmpeg 5.0+

## 2. Local Installation & Run
```bash
cd project_50_handwritten_document_recognition/source_code
pip install -r ../requirements.txt
python backend/train_idp_models.py
python run_system.py --port 5050
```

## 3. Verification
Verify gateway operational status:
```bash
curl http://127.0.0.1:5050/api/health/
```

Run test suite:
```bash
pytest tests/test_api_and_system.py -v
```

## 4. Operational Maintenance
- **SQLite WAL Checkpointing**:
```bash
sqlite3 data/idp.db "PRAGMA wal_checkpoint(TRUNCATE);"
```
