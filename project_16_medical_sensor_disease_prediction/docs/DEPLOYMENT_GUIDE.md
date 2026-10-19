# Deployment & Execution Guide

## 1. System Requirements
- **Operating System**: macOS (Darwin arm64/x86_64) or Linux (Ubuntu 20.04+).
- **Node.js**: v18.0.0 or higher.
- **Bun**: v1.1.0 or higher.
- **Python**: v3.10 or higher with `pip` and virtual environment support.

## 2. Port Configuration Summary
- **Frontend UI**: `http://localhost:5173`
- **Node.js Express Backend**: `http://localhost:5016`
- **Python 1D CNN Inference Engine**: `http://localhost:5017`

## 3. Step-by-Step Installation

### Step 1: Start Python Inference Microservice
```bash
cd source_code/ml-model
pip3 install -r requirements.txt
PORT=5017 python3 inference_service.py
```
Verify:
```bash
curl -s http://127.0.0.1:5017/health
```

### Step 2: Start Node.js Express Gateway
```bash
cd source_code/backend
npm install
cat << 'EOF' > .env
PORT=5016
NODE_ENV=development
FRONTEND_URL=http://localhost:5016,http://localhost:5173,http://localhost:8080,http://127.0.0.1:5016
DATABASE_PATH=./storage/medical.db
ECG_STORAGE_PATH=./storage/ecg
REPORTS_STORAGE_PATH=./storage/reports
MAX_UPLOAD_SIZE_MB=10
MODEL_SERVICE_URL=http://127.0.0.1:5017
EOF
npm start
```
Verify:
```bash
curl -s http://127.0.0.1:5016/api/system/status
```

### Step 3: Start TanStack / React Frontend
```bash
cd source_code/pixel-perfect-pixels
bun install
cat << 'EOF' > .env
VITE_API_BASE_URL=http://localhost:5016/api
EOF
bun run dev --port 5173
```
Open your browser to `http://localhost:5173`.
