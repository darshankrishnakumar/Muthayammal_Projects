# Enterprise Deployment Guide: Fruit Quality Grading Microservice

## 1. System Requirements
- Python 3.10+
- PyTorch 2.x (with Apple Silicon MPS / NVIDIA CUDA)
- FastAPI & Uvicorn
- SQLite 3 with WAL mode

## 2. Pinned Port Allocation
- **Assigned Port**: `5041`
- **Host**: `0.0.0.0` or `127.0.0.1`

## 3. Server Launch Command
```bash
cd project_41_fruit_quality_grading/source_code
PYTHONPATH=. python3 run_system.py --port 5041
```

## 4. Packhouse PLC Integration
- Connect optical line-scan cameras (1080p 60 FPS).
- Link pneumatic solenoid diverters via Modbus TCP.
- Mean end-to-end inference latency: ~14.8 ms.
