# Deployment Guide & Production Maintenance

## 1. Prerequisites
- **Operating System**: Linux (Ubuntu 22.04+ recommended) or macOS 13+ (Apple Silicon supported).
- **Python Runtime**: Python 3.10, 3.11, or 3.12.
- **Hardware**:
  - Minimum: Quad-core CPU, 8 GB RAM (CPU inference ~35ms).
  - Recommended: Apple Silicon M-series (MPS) or NVIDIA GPU (CUDA 11.8+ / 12.x, inference ~12ms).

## 2. Installation Steps
```bash
# Clone and navigate to project directory
cd project_20_weapon_detection

# Install Python backend dependencies
pip install -r source_code/backend/requirements.txt

# Verify model weights are present
ls -la source_code/backend/yolov8n.pt

# Execute automated test suite (36 tests)
python3 -m unittest discover -s source_code/tests -p "test_*.py" -v

# Launch the production service on Port 5020
python3 source_code/backend/app.py
```

## 3. Operational Verification
```bash
# Query health endpoint
curl -s http://127.0.0.1:5020/api/health | jq .

# Verify CCTV nodes
curl -s http://127.0.0.1:5020/api/cctv/cameras | jq .
```
Open `http://127.0.0.1:5020` in any web browser to open the VIGIL-8 Security Command Center.
