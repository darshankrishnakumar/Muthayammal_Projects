# Production Deployment & Installation Guide

## 1. System Requirements
- **Host OS**: macOS (Apple Silicon M1/M2/M3/M4) or Ubuntu Linux 22.04 LTS (x86_64 or ARM64).
- **Compute Accelerators**: Apple Metal Performance Shaders (MPS) or NVIDIA CUDA 12.x.
- **Python**: Version 3.10+ (Tested on 3.12).
- **Memory**: Minimum 4 GB RAM (8 GB recommended).
- **Storage**: 500 MB free disk space for SQLite database, models, and dependencies.

## 2. Fast Launch Instructions
```bash
# 1. Clone repository and navigate to source code
cd project_43_document_forgery_detection/source_code

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch microservice on Port 5043
PYTHONPATH=. python3 run_system.py --port 5043
```

## 3. Production Hardening
- Use reverse proxy (NGINX or Caddy) with TLS/SSL termination.
- Configure automatic SQLite backups via `.backup` or streaming replication.
- Integrate with document ingestion queues (Apache Kafka, RabbitMQ, or AWS SQS).
