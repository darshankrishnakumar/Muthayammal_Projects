# 06. REST API Specification

**Base URL:** `http://127.0.0.1:5022/api`

### 1. Health & Model Status
`GET /api/health`
```json
{
  "status": "healthy",
  "service": "AI Customer Complaint & Priority Router API",
  "model": "Logistic Regression (Calibrated L2 Regularized)",
  "accuracy_pct": 100.0,
  "macro_f1": 1.0,
  "categories_supported": 6,
  "total_tickets_logged": 15,
  "database": "SQLite 3 (Transactional ACID)"
}
```

### 2. Triage Customer Complaint
`POST /api/classify`  
**Request Payload:**
```json
{
  "complaint": "My corporate card was charged $1,490 twice for order #88492. I need an immediate reversal and refund! Unauthorized charge."
}
```
**Response (200 OK):**
```json
{
  "id": 16,
  "timestamp": "2026-10-19 19:35:00",
  "complaint": "My corporate card was charged $1,490 twice for order #88492...",
  "category": "payment_issue",
  "category_label": "Payment & Billing Dispute",
  "category_icon": "💳",
  "department": "FinOps Billing & Fraud Team",
  "priority": "critical",
  "priority_label": "CRITICAL",
  "confidence": 0.9825,
  "probabilities": {
    "payment_issue": 0.9825,
    "account_issue": 0.0082,
    "service_dissatisfaction": 0.0041,
    "technical_issue": 0.0022,
    "delivery_problem": 0.0018,
    "product_complaint": 0.0012
  },
  "urgency_score": 94,
  "sentiment_score": -0.85,
  "sla_hours": 0.5,
  "sla_deadline": "2026-10-19 20:05 UTC",
  "status": "PENDING"
}
```

### 3. List Complaints
`GET /api/complaints?limit=50&category=payment_issue&priority=critical`

### 4. Update Ticket Status
`POST /api/tickets/<id>/status`  
**Payload:**
```json
{
  "status": "RESOLVED",
  "notes": "Refund processed via Stripe gateway batch #88492-R"
}
```

### 5. Aggregate Operational Statistics
`GET /api/stats`

### 6. Departmental Queue Loads
`GET /api/departments`

### 7. System Audit Trail
`GET /api/audit?limit=25`

### 8. Executive Dossier Report
`GET /api/export/report`
