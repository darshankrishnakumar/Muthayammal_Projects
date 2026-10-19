# REST API Reference & Specification

PROJECT-017 provides a complete RESTful JSON API on Port 5017.

## Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | GET | Renders main interactive web application dashboard |
| `GET /health` | GET | Service status, port allocation, and architecture metadata |
| `POST /api/predict` | POST | Performs multilevel scan, logs to SQLite, returns probabilities |
| `GET /api/history` | GET | Retrieves historical scan records from SQLite |
| `GET /api/stats` | GET | Aggregates total scans, threat count, threat rate, and average latency |
| `GET /api/benchmark` | GET | Comparative metrics for all 9 evaluated architectures |
| `GET /api/samples` | GET | 6 pre-configured academic email threat benchmarks |

---

### `POST /api/predict`
Executes real-time inference across structural headers and email body text.

**Request Payload:**
```json
{
  "from": "security-alert@chase-secure-verify.com",
  "reply_to": "fraud-harvest@server-host.xyz",
  "spf_dkim": "fail",
  "subject": "URGENT: Immediate Account Suspension - Verification Required",
  "email_text": "Dear Valued Customer, verify your credentials at http://chase-secure-verify.com/login",
  "model": "rcnn_attn"
}
```

**Response Body (200 OK):**
```json
{
  "status": "success",
  "data": {
    "scan_id": 24,
    "prediction": "Phishing Email",
    "is_phishing": true,
    "phishing_probability": 99.9,
    "safe_probability": 0.1,
    "threat_level": "CRITICAL / PHISHING CONFIRMED",
    "risk_class": "danger",
    "latency_ms": 12.19,
    "consensus": "6/9 Models Flagged Phishing",
    "multilevel_breakdown": {
      "header_risk": 90.0,
      "body_risk": 99.9,
      "header_anomalies_detected": 3,
      "char_word_features_processed": 13
    },
    "token_attention_heatmap": [
      {"word": "urgent", "attention_score": 49.7, "is_threat_token": true},
      {"word": "account", "attention_score": 77.4, "is_threat_token": true},
      {"word": "verification", "attention_score": 82.2, "is_threat_token": false},
      {"word": "verify", "attention_score": 75.8, "is_threat_token": true}
    ]
  }
}
```
