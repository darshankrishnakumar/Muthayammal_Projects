# 06. REST API Specification

**Base URL:** `http://127.0.0.1:5023/api`

### 1. Health & Model Status
`GET /api/health`
```json
{
  "status": "healthy",
  "service": "AI Meeting Summarization & Action-Item Extraction API",
  "model": "Logistic Regression (Calibrated L2 Regularized)",
  "dialogue_act_accuracy_pct": 100.0,
  "priority_accuracy_pct": 72.64,
  "total_meetings_indexed": 10,
  "database": "SQLite 3 (Transactional ACID)"
}
```

### 2. Summarize Meeting Transcript
`POST /api/summarize`  
**Request Payload:**
```json
{
  "title": "Q3 Cloud Architecture Review",
  "transcript": "[Sarah]: Let's review the Q3 architecture.
[Marcus]: I will optimize the database index by tomorrow.
[Elena]: We decided to approve Kafka as standard messaging."
}
```
**Response (200 OK):**
```json
{
  "id": 11,
  "title": "Q3 Cloud Architecture Review",
  "executive_summary": "The session focused on q3 cloud architecture review with active contributions across 3 participants...",
  "summary_bullets": [
    "Session convened to address key roadmap decisions...",
    "Identified 1 high-impact action items with clear ownership...",
    "Reached definitive consensus on 1 architectural decisions."
  ],
  "action_items": [
    {
      "task": "I will optimize the database index by tomorrow.",
      "assignee": "Marcus",
      "priority": "Critical",
      "category": "Architecture",
      "deadline": "Tomorrow 10 AM",
      "status": "OPEN"
    }
  ],
  "decisions": [
    "We decided to approve Kafka as standard messaging."
  ],
  "word_count": 27,
  "duration_est_mins": 2.0,
  "engagement_score": 88.5,
  "sentiment_index": 0.82
}
```

### 3. List Meetings
`GET /api/meetings?limit=25`

### 4. Single Meeting Details
`GET /api/meetings/<id>`

### 5. Update Action Item Status
`POST /api/actions/<id>/status`  
`{"status": "COMPLETED"}`

### 6. Operational Statistics
`GET /api/stats`

### 7. Export Markdown Minutes
`GET /api/export/minutes/<id>`
