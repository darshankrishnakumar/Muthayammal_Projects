# Enterprise Deployment Guide: Pavement Crack Microservice

## 1. Prerequisites
- Python 3.10+
- PyTorch 2.x
- FastAPI & Uvicorn
- SQLite 3 with WAL support

## 2. Pinned Port Allocation
- **Assigned Port**: `5038`
- **Host**: `127.0.0.1` or `0.0.0.0`

## 3. Launch Command
```bash
python3 source_code/run_system.py --port 5038
```

## 4. Edge Vehicle Integration (NVIDIA Jetson)
- Connect 50 Hz linescan camera feed via RTSP or USB3 Vision.
- Enable PyTorch FP16 execution: `model.half().to('cuda')`.
- Latency per scan frame: ~4.2 ms on Jetson Orin Nano.
