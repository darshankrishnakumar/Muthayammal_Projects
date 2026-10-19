# 06. REST API Specification

The backend exposes a comprehensive set of RESTful endpoints on `http://127.0.0.1:5024`:

### 1. Health Status
- **Endpoint:** `GET /api/health`
- **Response:**
```json
{
  "database_backend": "SQLite ACID Relational Graph DB (fraud_graph.db)",
  "detected_syndicates": ["Transnational Circular Carousel Loop Alpha", ...],
  "edges_tracked": 1650,
  "frozen_accounts": 0,
  "model": "2-Layer Graph Convolutional Network (GCN + GraphSAGE Pool)",
  "nodes_tracked": 520,
  "service": "Financial Fraud Graph Neural Network (GNN) Engine",
  "status": "healthy"
}
```

### 2. Graph Topology
- **Endpoint:** `GET /api/graph`
- **Response:** Complete JSON object containing `nodes` array, `edges` array, and graph `metadata`.

### 3. Detected Syndicates
- **Endpoint:** `GET /api/graph/syndicates`
- **Response:** Array of syndicates with pattern, risk_score, involved_volume_usd, nodes, edges, and descriptions.

### 4. Forensic Node Details
- **Endpoint:** `GET /api/node/<nid>`
- **Response:** Account details, inbound/outbound transactions, volume, and `gnn_message_passing` explanation.

### 5. Account Freeze Sanction
- **Endpoint:** `POST /api/account/freeze`
- **Payload:** `{"account_id": "ACC-0101", "reason": "AML Sanction"}`
- **Response:** `{"success": true, "account_id": "ACC-0101", "status": "FROZEN"}`

### 6. Account Unfreeze
- **Endpoint:** `POST /api/account/unfreeze`
- **Payload:** `{"account_id": "ACC-0101"}`
- **Response:** `{"success": true, "account_id": "ACC-0101", "status": "UNFROZEN"}`

### 7. Synthetic Ring Injection
- **Endpoint:** `POST /api/simulate/ring`
- **Response:** `{"success": true, "ring_id": 801, "nodes_added": [...], "edges_added": [...]}`

### 8. FinCEN Regulatory SAR Export
- **Endpoint:** `GET /api/export/sar`
- **Response:** Standardized SAR compliance filing dossier.\n