# API Specification: Skill-Gap Analysis Microservice (Port 5045)

## Base URL
`http://127.0.0.1:5045/`

## Core Endpoints

### 1. System Health Check
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 45 | AI-Powered Skill-Gap Analysis & Career Recommendation Platform",
  "port": 5045,
  "database": {
    "mode": "SQLite WAL",
    "connected": true,
    "url": "sqlite:///.../career.db"
  },
  "hardware": {
    "device": "mps",
    "cuda_available": false,
    "mps_available": true
  },
  "models": {
    "competency_embedding_net": "CompetencyEmbeddingNet (64-D Latent Competency Vector Space)",
    "trajectory_forecast_net": "CareerTrajectoryForecastNet (10-in, 4-head Multi-Target Neural Regressor)"
  }
}
```

### 2. Available Career Roles
- **Route**: `GET /api/career/roles`
- **Response**: Returns list of all active target career pathways with competency requirements and market compensation.

### 3. Generate Upskilling Roadmap
- **Route**: `POST /api/career/analyze`
- **Request Body**:
```json
{
  "user_name": "Jordan Bell",
  "current_skills": "Python, PyTorch, Deep Learning, Docker",
  "target_role_id": "ROLE-AI",
  "years_experience": 4.0,
  "certifications_count": 2,
  "completed_projects": 5,
  "weekly_hours": 14,
  "learning_budget": 1200.0
}
```
- **Response**:
```json
{
  "status": "SUCCESS",
  "roadmap": {
    "roadmap_id": "RMAP-2026-F8A12C",
    "user_name": "Jordan Bell",
    "target_role": "AI / ML Research & Platform Engineer",
    "readiness_score": 85.7,
    "gap_score": 14.3,
    "missing_skills": "Transformers, MLOps",
    "recommended_courses": "DeepLearning.AI HuggingFace Specialization...",
    "recommended_projects": "Fine-Tuning LLaMA-3 for Domain Q&A...",
    "estimated_weeks_to_readiness": 6,
    "salary_growth_potential": 42.5,
    "evidence_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "metrics": { ... }
}
```

### 4. Cryptographic Audit Ledger
- **Route**: `GET /api/career/audit-logs?limit=50`
- **Response**: Returns chained blocks with SHA-256 hashes and previous hash pointers.

### 5. System Analytics Summary
- **Route**: `GET /api/analytics/summary`
- **Response**: Aggregated roadmap count, mean readiness, and neural model benchmarks.
