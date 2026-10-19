# Deployment & Production Runbook

## 1. Quick Launch
```bash
# Set dedicated port 5019
export PORT=5019
python3 source_code/backend/app.py
```
Open `http://localhost:5019` in any web browser.

## 2. Production Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=5019
EXPOSE 5019
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5019", "source_code.backend.app:app"]
```

## 3. Environment Variables
- `PORT`: TCP listening port (default: `5019`).
- `DATABASE_URL`: SQLAlchemy connection URI (default: `sqlite:///stock_management.db`).
- `FLASK_ENV`: Environment mode (`production` or `development`).
