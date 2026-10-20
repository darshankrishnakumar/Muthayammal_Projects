# Enterprise Deployment Guide: Industrial Fire & Smoke Microservice

## 1. System Requirements
- Python 3.10+
- PyTorch 2.x (with MPS / CUDA acceleration)
- FastAPI & Uvicorn
- SQLite 3 with WAL mode

## 2. Pinned Port Allocation
- **Assigned Port**: `5040`
- **Host**: `0.0.0.0` or `127.0.0.1`

## 3. Server Launch Command
```bash
cd project_40_fire_smoke_detection/source_code
PYTHONPATH=. python3 run_system.py --port 5040
```

## 4. Edge Appliance Deployment (NVIDIA Jetson / Mac mini)
- Connect RTSP IP cameras (1080p 60 FPS).
- Set `device = 'mps'` or `'cuda'`.
- Mean end-to-end inference latency: ~16.4 ms.
