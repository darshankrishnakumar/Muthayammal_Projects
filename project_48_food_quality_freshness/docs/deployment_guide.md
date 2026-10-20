# Deployment Guide — PROJECT-048
## Production Launch on Dedicated Port 5048

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- PyTorch 2.0+ (with Apple Silicon MPS or NVIDIA CUDA support)
- SQLite 3.35+

### 2. Starting the Platform
```bash
# 1. Free Port 5048 if previously occupied
lsof -ti :5048 | xargs kill -9 2>/dev/null || true

# 2. Run the application
PYTHONPATH=source_code python3 source_code/run_system.py --port 5048
```

### 3. Verification Commands
```bash
# Check health endpoint
curl -s http://localhost:5048/api/health/

# Verify audit chain integrity
curl -s http://localhost:5048/api/freshness/audit-logs | jq .chain_verified

# Run automated QA test suite
PYTHONPATH=source_code python3 -m unittest source_code/tests/test_api_and_system.py
```
