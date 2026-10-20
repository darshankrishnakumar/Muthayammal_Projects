# REST API Specification: Classroom Engagement Analytics (Port 5047)

## System Health
- **Route**: `GET /api/health` and `GET /api/health/`
- **Response**:
  ```json
  {
    "status": "HEALTHY",
    "service": "Project 47 Classroom Engagement Analytics API",
    "port": 5047,
    "database": "SQLite (WAL Mode Enabled)",
    "hardware_device": "mps",
    "models": {
      "multimodal_engagement_net": "MultimodalEngagementNet (Loaded)",
      "attention_forecast_regressor": "AttentionForecastRegressorNet (Loaded)"
    }
  }
  ```

## Sessions & Timeline
- **Route**: `GET /api/engagement/sessions`
- **Route**: `GET /api/engagement/timeline?skip=0&limit=50`
- **Route**: `GET /api/engagement/audit-logs?limit=50`
- **Route**: `GET /api/engagement/stats`
- **Route**: `GET /api/analytics/summary`

## Synchronous Multimodal Evaluation
- **Route**: `POST /api/engagement/analyze` (and alias `POST /api/engagement/evaluate`)
- **Request Body**:
  ```json
  {
    "course_code": "CS-301",
    "lecture_title": "Consensus Protocols",
    "student_count": 32,
    "attentive_pct": 85.0,
    "bored_pct": 6.0,
    "distracted_pct": 6.5,
    "drowsy_pct": 2.5,
    "head_pose_board_focus_pct": 88.0,
    "hand_raise_count": 5
  }
  ```
- **Response Body**:
  ```json
  {
    "status": "SUCCESS",
    "snapshot": {
      "snapshot_id": "ENG-2026-A1B2C3",
      "mean_engagement_score": 86.4,
      "pedagogical_recommendation": "MAINTAIN_CURRENT_PACE",
      "drowsiness_risk_score": 3.2,
      "evidence_hash": "..."
    },
    "metrics": { ... },
    "audit_block_index": 3
  }
  ```
