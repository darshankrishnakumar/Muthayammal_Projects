# Troubleshooting & Maintenance Guide

## Common Issues & Resolutions

### 1. Port 5040 Already in Use
- Check active process: `lsof -i :5040`
- Terminate stale process: `kill -9 <PID>`

### 2. High Industrial Dust / Steam False Alarms
- Ensure temporal FFT flicker gating is active.
- Dust and steam lack periodic 5-20 Hz vortex shedding oscillations and are mathematically rejected.

### 3. Trailing Slash API Route Handling
- Both `/api/health` and `/api/health/` are explicitly routed via dual decorators.
