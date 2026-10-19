# 02. System Requirements & Domain Scope

## Functional Requirements
1. **Natural Language Text Ingestion:**
   - Multi-channel intake accepting unstructured text from web portal, REST API endpoints, and webhook events.
   - Text preprocessing: Unicode normalization, lowercase conversion, punctuation filtering, and stop-word removal.

2. **Multi-Class Category Classification (Head 1):**
   - Precise routing to six operational departments based on semantic intent.
   - Output calibrated posterior class probability distribution summing to 1.0.
   - Extract top discriminatory n-gram keywords for operator explainability.

3. **Multi-Tier Priority Prediction (Head 2):**
   - Classify urgency into four standardized tiers: Critical, High, Medium, Low.
   - Dynamic SLA calculation: 0.5 hours (Critical), 2.0 hours (High), 8.0 hours (Medium), 24.0 hours (Low).
   - Compute absolute UTC resolution deadlines based on ticket timestamp.

4. **Sentiment & Urgency Analytics:**
   - Deterministic urgency scoring scaled from 10 to 100 based on predicted priority and model confidence.
   - Continuous sentiment index ranging from -1.0 (severe hostility/distress) to +0.25 (calm informational inquiry).

5. **Transactional Persistence & Auditing:**
   - Store all ingested tickets, NLP metadata, and lifecycle statuses in SQLite 3.
   - Maintain an append-only `system_audit` table tracking every transaction with IP, timestamp, and outcome.

6. **Interactive Management Cockpit:**
   - Real-time Chart.js donut and horizontal bar charts.
   - Searchable, filterable ticket stream table with status update capabilities.
   - Single-click CSV report export.

## Non-Functional Requirements
- **Inference Latency:** < 5 milliseconds per ticket on standard CPU hardware.
- **Hardware Footprint:** Zero GPU requirement, < 50 MB total RAM utilization.
- **Port Assignment:** Strict dedicated Port 5022 binding.
- **Availability & Robustness:** Handled fallback training if serialized artifacts are deleted; comprehensive error handling on malformed JSON or empty strings.
