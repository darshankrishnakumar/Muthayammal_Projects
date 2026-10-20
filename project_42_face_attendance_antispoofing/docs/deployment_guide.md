# Production Deployment & Turnstile Installation Guide

## 1. System Requirements
- **Host OS**: macOS (Apple Silicon M1/M2/M3/M4) or Ubuntu Linux 22.04 LTS (x86_64 or ARM64).
- **Compute Accelerators**: Apple Metal Performance Shaders (MPS) or NVIDIA CUDA 12.x.
- **Python**: Version 3.10+ (Tested on 3.12).
- **Memory**: Minimum 4 GB RAM (8 GB recommended).
- **Storage**: 500 MB free disk space for SQLite database, models, and dependencies.

## 2. Fast Launch Instructions
```bash
# 1. Clone repository and navigate to source code
cd project_42_face_attendance_antispoofing/source_code

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch microservice on Port 5042
PYTHONPATH=. python3 run_system.py --port 5042
```

## 3. Edge Turnstile GPIO & Relay Wiring
- **Relay Pin**: Connect GPIO Pin 17 (or USB Relay Board Channel 1) to the Turnstile Motor Controller 'OPEN_COMMAND' terminal.
- **Pulse Duration**: Configure pulse hold time to 250 milliseconds.
- **Fail-Secure Architecture**: Ensure relays are wired in Normally Open (NO) configuration so power loss leaves turnstiles locked.
