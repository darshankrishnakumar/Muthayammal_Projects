# REST API Reference & Endpoint Specification

Host Address: `http://127.0.0.1:5021`

## 1. System Health & Metadata
- **`GET /api/health`**
  - **Returns**: `status`, `service`, `port`, `models_loaded`, `dataset`, `database`, `active_transactions`, `blocked_cards_count`.

## 2. Fraud Prediction & Telematics
- **`POST /api/predict`**
  - **Payload**: `{"merchant": "Target", "amount": 45.20, "time": 43200, "features": {"V14": -5.2, "V4": 4.1}, "threshold": 0.50}`
  - **Returns**: `risk_score`, `fraud_probability`, `is_fraud`, `decision`, `risk_level`, `recommended_action`, `top_drivers`, `all_attributions`.
- **`GET /api/stream/next`**
  - **Returns**: Next simulated streaming transaction with real-time risk assessment and database commit.
- **`POST /api/batch/evaluate`**
  - **Payload**: `{"threshold": 0.50, "transactions": [...]}`
  - **Returns**: Evaluated array summary, fraud percentage, and itemized decisions.

## 3. Account Sanctions & Card Blacklist
- **`POST /api/card/block`**: `{"card_id": "CARD-4891-3419", "reason": "Compromised account"}`
- **`POST /api/card/unblock`**: `{"card_id": "CARD-4891-3419"}`
- **`GET /api/blocked-cards`**: Returns list of all sanctioned card accounts.

## 4. Benchmarks & Governance
- **`GET /api/transactions`**: Returns transaction ledger with optional `?limit=` filter.
- **`GET /api/models`**: Returns comparative benchmarks across RF, GBM, and Neural models.
- **`GET /api/metrics`**: Returns confusion matrix and ROC curve points for given `?threshold=`.
- **`GET /api/stats`**: Returns real-time KPI totals and fraud ratios.
- **`GET /api/audit`**: Returns system audit events.
- **`GET /api/dataset/sample`**: Returns representative rows from 10,000 transaction CSV.
- **`GET /api/export/report`**: Exports comprehensive forensic JSON audit dossier.
