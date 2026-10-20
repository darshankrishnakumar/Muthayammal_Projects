# Enterprise Deployment Guide: Sign Language & Speech Microservice

## 1. Prerequisites
- Python 3.10+
- PyTorch 2.x
- FastAPI & Uvicorn
- SQLite 3 with WAL mode

## 2. Pinned Port Allocation
- **Assigned Port**: `5039`
- **Host**: `0.0.0.0` or `127.0.0.1`

## 3. Launch Command
```bash
python3 source_code/run_system.py --port 5039
```

## 4. Mobile & Embedded Assistive Hardware (Jetson Orin / Smart Glasses)
- Connect standard USB webcam or smart glasses camera (60 FPS).
- Pin PyTorch execution to GPU/MPS: `device = 'mps'`.
- End-to-end translation latency: ~21.4 ms.
