# 02. System Requirements Specification (PROJECT-026)

## Functional Requirements (FR)
- **FR-1 [Packet Flow Ingestion]:** Ingest and parse network flow telemetry capturing duration, source/destination payload bytes, connection counts, error rates, and port statistics.
- **FR-2 [Unsupervised Anomaly Reconstruction]:** Execute deep autoencoder forward pass on every flow to compute Euclidean reconstruction error $L_2(x) = rac{1}{D} \sum_{i=1}^D (x_i - \hat{x}_i)^2$.
- **FR-3 [Zero-Day Anomaly Trigger]:** If $L_2(x) > 	au$ ($	au = 0.00932$), automatically classify the flow as `ZeroDay_Anomaly` and assign `SANDBOX_ISOLATE` containment action.
- **FR-4 [Multi-Class Signature Classification]:** Evaluate 17-dimensional enriched feature representations across 7 verified categories: Normal, DoS SYN Flood, Probe PortScan, R2L SSH Brute Force, Botnet Mirai C2, U2R Buffer Overflow, and Zero-Day Anomaly.
- **FR-5 [Autonomous Defense & Quarantine]:** On detecting critical threats, automatically blacklist hostile IP in SQLite database and generate `iptables`, `ufw`, and AWS NACL drop commands.
- **FR-6 [Relational Persistence]:** Maintain ACID-compliant audit logs and flow records in SQLite `network_nids.db`.
- **FR-7 [Real-Time Web Radar]:** Provide an interactive 360-degree HTML5 canvas radar sweeping at 60 fps with color-coded target blips.

## Non-Functional Requirements (NFR)
- **NFR-1 [Inference Latency]:** End-to-end neural forward pass must complete under 2.5 milliseconds per flow on standard commodity CPU hardware.
- **NFR-2 [Throughput]:** Backend streaming pipeline must sustain at least 500 packets per second without memory leakage.
- **NFR-3 [Classification Reliability]:** Macro F1-score must exceed 0.98 across unseen benchmark test splits.
- **NFR-4 [Concurrency & Lock Safety]:** Database operations must operate in WAL mode with 30-second busy timeout to eliminate lock contention.
