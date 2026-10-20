# API Specification: Resume Screening & Job Matching Microservice (Port 5044)

## Base URL
`http://127.0.0.1:5044/`

## Core Endpoints

### 1. System Health Check
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 44 | Intelligent Resume Screening & Contextual Job Matching Engine",
  "port": 5044,
  "database": {
    "mode": "SQLite WAL",
    "connected": true,
    "url": "sqlite:///.../resume_matching.db"
  },
  "hardware": {
    "device": "mps",
    "cuda_available": false,
    "mps_available": true
  },
  "models": {
    "transformer_matcher": "TransformerSemanticMatcherNet (128-D Contextual Cross-Attention)",
    "competency_regressor": "CandidateCompetencyRegressorNet (10-in, 4-head Multi-Target)"
  }
}
```

### 2. Job Openings Requisition
- **Route**: `GET /api/screening/jobs`
- **Response**: Returns list of all active institutional job requisitions.

### 3. Screen Candidate Resume
- **Route**: `POST /api/screening/match`
- **Request Body**:
```json
{
  "candidate_name": "Dr. Sarah Connor",
  "candidate_skills": "PyTorch, Transformers, Computer Vision, Docker, FastAPI, Python",
  "experience_years": 6.5,
  "job_id": "JOB-AI-LEAD",
  "certification_count": 3,
  "education_level": 3,
  "github_contributions": 72,
  "anonymize_bias": false
}
```
- **Response**:
```json
{
  "status": "SUCCESS",
  "match": {
    "match_id": "MAT-2026-F8A12C",
    "job_id": "JOB-AI-LEAD",
    "candidate_name": "Dr. Sarah Connor",
    "overall_match_score": 96.4,
    "semantic_similarity": 0.965,
    "skill_coverage_pct": 100.0,
    "experience_fit_score": 9.8,
    "seniority_compatibility": 97.2,
    "screening_decision": "SHORTLISTED",
    "evidence_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "metrics": { ... }
}
```

### 4. Cryptographic Audit Ledger
- **Route**: `GET /api/screening/audit-logs?limit=50`
- **Response**: Returns chained blocks with SHA-256 hashes and previous hash pointers.

### 5. System Analytics Summary
- **Route**: `GET /api/analytics/summary`
- **Response**: Aggregated applicant volume, shortlist ratio, and model benchmark statistics.
