# Production Deployment & Operations Guide

## Requirements
- Python 3.10+
- FastAPI 0.100+
- Uvicorn 0.22+
- Scikit-Learn 1.3+
- Pandas 2.0+
- SQLite3

## Quickstart Commands
```bash
# 1. Navigate to project root
cd project_18_dress_recommendation_skin_tone

# 2. Start production FastAPI server on Port 5018
python3 -m uvicorn source_code.server:app --host 0.0.0.0 --port 5018
```

## Health Verification
```bash
curl -s http://127.0.0.1:5018/health
```
