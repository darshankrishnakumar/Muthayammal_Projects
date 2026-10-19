# 08. Production Deployment Guide (PROJECT-028)

## System Requirements
- Python 3.10 or higher
- RAM: 2 GB minimum (model footprints occupy ~50 MB RAM)
- Storage: 100 MB free disk space

## Quick Start
```bash
# 1. Navigate to project root
cd project_28_air_quality_forecast

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Generate dataset & train deep models
python3 source_code/data/generate_aqi_dataset_and_models.py

# 4. Launch backend service on Port 5028
python3 source_code/backend/app.py
```

## Verification
Confirm the service is active by querying the health endpoint:
```bash
curl http://127.0.0.1:5028/api/health
```

The interactive Air Quality Dashboard is accessible in your web browser at:
`http://127.0.0.1:5028/`
