# Industrial Edge Deployment Guide (Port 5046)

## 1. Prerequisites
- Python 3.10+
- PyTorch with MPS (macOS) or CUDA (Linux/NVIDIA)
- SQLite 3.35+ (WAL mode supported)
- Modern Web Browser (Chrome, Firefox, Safari)

## 2. Launching the Microservice
```bash
cd project_46_manufacturing_defect_detection/source_code
PYTHONPATH=. python3 run_system.py --port 5046
```

## 3. Industrial Fieldbus Integration
- **OPC-UA**: Mount microservice REST endpoints into OPC-UA Server address space.
- **PLC Trigger**: Digital input signal (24V sink/source) triggers `/api/inspection/scan`.
- **Digital Output**: Relay closure directs pneumatic ejector solenoid valve.
