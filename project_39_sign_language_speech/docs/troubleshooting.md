# Troubleshooting & Maintenance Guide

## Common Issues & Resolutions

### 1. Port 5039 Already in Use
- Check active process: `lsof -i :5039`
- Terminate stale process: `kill -9 <PID>`

### 2. MediaPipe Landmark Occlusion
- Ensure adequate lighting and camera positioning capturing both hands and torso.
- System automatically applies temporal interpolation over isolated dropped frames.

### 3. Trailing Slash API Route Handling
- Both `/api/health` and `/api/health/` are explicitly routed via dual decorators.
