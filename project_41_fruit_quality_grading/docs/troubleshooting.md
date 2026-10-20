# Troubleshooting & Maintenance Guide

## Common Issues & Resolutions

### 1. Port 5041 Already in Use
- Check active process: `lsof -i :5041`
- Terminate stale process: `kill -9 <PID>`

### 2. High Ambient Illumination Variation
- Standardize packhouse inspection tunnel with diffuse LED dome lighting to prevent specular reflection glare.

### 3. Trailing Slash API Route Handling
- Both `/api/health` and `/api/health/` are explicitly routed via dual decorators.
