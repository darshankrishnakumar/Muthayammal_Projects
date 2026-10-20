# Enterprise Deployment Guide: Project 44 Microservice

## Port Allocation
Project 44 is allocated dedicated **Port 5044** (`http://127.0.0.1:5044/`).

## Quickstart Launch

```bash
# 1. Navigate to source code directory
cd project_44_resume_screening_nlp/source_code

# 2. Activate Python environment and initialize dependencies
export PYTHONPATH=.

# 3. Launch the high-concurrency microservice
python3 run_system.py --port 5044
```

## System Verification

```bash
# Check service health and MPS hardware binding
curl -s http://127.0.0.1:5044/api/health | jq .

# Verify active job requisitions
curl -s http://127.0.0.1:5044/api/screening/jobs | jq .
```
