# Campus Edge Deployment Guide (Port 5047)

## 1. Prerequisites
- Python 3.10+
- PyTorch with MPS (macOS) or CUDA (Linux/NVIDIA)
- SQLite 3.35+ (WAL mode supported)
- Modern Web Browser (Chrome, Firefox, Safari)

## 2. Launching the Microservice
```bash
cd project_47_classroom_engagement_analysis/source_code
PYTHONPATH=. python3 run_system.py --port 5047
```

## 3. Lecture Hall Integration
- **Camera Mounting**: Wide-angle PTZ camera positioned at front of room facing cohort.
- **Edge Mini-PC**: Local processing on Apple Silicon Mac Mini or Intel NUC inside podium.
- **LMS Sync**: Synchronize aggregate session metrics to Canvas or Blackboard gradebook.
