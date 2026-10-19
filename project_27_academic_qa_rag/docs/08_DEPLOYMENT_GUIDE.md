# 08. Production Deployment Guide (PROJECT-027)

## Prerequisites
- Python 3.10 or higher
- System RAM: 2 GB minimum (models and vector indexes occupy ~50 MB RAM)
- Disk Storage: 100 MB free disk space

## Quick Start
```bash
# 1. Navigate to project root
cd project_27_academic_qa_rag

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Build corpus & train dense bi-encoder weights
python3 source_code/data/generate_corpus_and_embeddings.py

# 4. Launch backend server on Port 5027
python3 source_code/backend/app.py
```

## Verification
Verify the server is running by requesting the health check:
```bash
curl http://127.0.0.1:5027/api/health
```

The Web QA Portal is accessible in your web browser at:
`http://127.0.0.1:5027/`
