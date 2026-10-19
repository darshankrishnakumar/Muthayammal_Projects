# Project 31: Requirements Specification

## 1. Functional Requirements (FR)
- **FR-01 (Hydrological Ingestion)**: Ingest 8-dimensional telemetry vectors (rainfall mm, river stage m, threshold m, soil moisture %, storm surge m, DEM elevation, drainage score, crest exceedance ratio).
- **FR-02 (4-Tier Alert Severity)**: Classify incoming catchment states into NORMAL, ADVISORY, WARNING, or CRITICAL tiers.
- **FR-03 (Inundation Depth Prediction)**: Numerically predict standing surface floodwater depth (meters) with strict non-negative boundary constraints.
- **FR-04 (Evacuation Lead-Time)**: Forecast hours until flood crest peak (1 to 24 hours) for timely civic response.
- **FR-05 (Emergency Dispatch Action)**: Support recording of civil defense deployments, flood barrier setups, and evacuation broadcasts.
- **FR-06 (ACID Relational Storage)**: Persist all assessments, telemetry, and dispatches in SQLite with Write-Ahead Logging (WAL).

## 2. Non-Functional Requirements (NFR)
- **NFR-01 (Inference Latency)**: End-to-end forward pass latency $< 10$ milliseconds on CPU.
- **NFR-02 (Detection Accuracy)**: Classification accuracy $> 90\%$ on held-out test data with high recall on critical deluge events.
- **NFR-03 (High Concurrency)**: SQLite WAL mode (`PRAGMA journal_mode=WAL;`) ensuring non-blocking reads during peak hazard alerting.
- **NFR-04 (Port Consistency)**: Operates strictly on allocated network port 5031.
