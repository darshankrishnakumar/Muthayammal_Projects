# Enterprise Deployment Guide: Project 45 Microservice

## Port Allocation
Project 45 is allocated dedicated **Port 5045** (`http://127.0.0.1:5045/`).

## Quickstart Launch

```bash
# 1. Navigate to source code directory
cd project_45_skill_gap_career_recommendation/source_code

# 2. Activate Python environment and initialize dependencies
export PYTHONPATH=.

# 3. Launch the high-concurrency microservice
python3 run_system.py --port 5045
```

## System Verification

```bash
# Check service health and MPS hardware binding
curl -s http://127.0.0.1:5045/api/health | jq .

# Verify active career roles
curl -s http://127.0.0.1:5045/api/career/roles | jq .
```
