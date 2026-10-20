# Troubleshooting & Maintenance Guide

## Common Issues & Resolutions

### 1. Port 5038 Already in Use
- Check active process: `lsof -i :5038`
- Terminate stale process: `kill -9 <PID>`

### 2. PyTorch MPS vs CPU Tensors
- Ensure all input tensors match `pavement_engine.device`:
  `tensor = tensor.to(engine.device)`

### 3. Trailing Slash API 404
- FastAPI router supports both `/api/health` and `/api/health/` via dual-route annotations.
