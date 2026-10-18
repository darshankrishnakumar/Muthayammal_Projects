# System Architecture & Technical Design

## High-Level Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Client Layer (Browser)                         │
│  - Vanilla HTML5 / Modern Cyberpunk SOC Glassmorphism UI               │
│  - Tabbed Workflow: Packet Inspector, Benchmarks, Event Logs, Analytics│
│  - Real-Time Async REST Client (Fetch API)                            │
└─────────────────────────────────▲──────────────────────────────────────┘
                                  │ HTTP / JSON (Port 5002)
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Application Gateway (FastAPI Layer)                  │
│  - CORS Middleware & Static File Mounting                              │
│  - Pydantic v2 Request Validation & Schema Serialization               │
│  - Endpoints: /health, /api/presets, /api/inspect, /api/events, etc.   │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│        Dual Machine Learning Engine  │ │        Database Subsystem     │
│  - Preprocessor (ColumnTransformer)  │ │  - SQLite3 Engine (nids.db)   │
│    • StandardScaler (Cont. Features) │ │  - Schema: security_events    │
│    • OneHotEncoder (Categoricals)    │ │  - Async Logging of Events    │
│    • Dimension: 111 Features         │ │  - Threat Analytics Engine    │
│  - Supervised Ensemble:              │ │    (Breakdowns, rates, avg ms)│
│    • Random Forest (100 Trees)       │ └───────────────────────────────┘
│    • Extra Trees (100 Trees)         │
│    • Weighted Soft-Voting Consensus  │
│  - Unsupervised Anomaly Engine:      │
│    • Isolation Forest (Contam=0.18)  │
│    • Out-of-Distribution Path Metric │
└──────────────────────────────────────┘
```

## Data Flow & Processing Pipeline

1. **Packet Ingestion**: The edge proxy or user specifies connection metrics (Source/Destination IP, protocol type, service, flag, duration, byte counters, error rates, and connection density).
2. **Schema Validation**: FastAPI validates input using `PacketInspectionRequest` Pydantic model:
   - Protocol types: `tcp`, `udp`, `icmp`.
   - Error rates bounded to $[0.0, 1.0]$.
   - Non-negative integer constraints for counts and durations.
3. **Feature Preprocessing**:
   - Continuous inputs scaled to zero mean and unit variance via `StandardScaler`.
   - Categorical inputs expanded via `OneHotEncoder` (`handle_unknown='ignore'`).
   - Combined feature vector: $\mathbf{x} \in \mathbb{R}^{111}$.
4. **Supervised Multi-Class Inference**:
   - Random Forest (100 trees) and Extra Trees (100 trees) evaluate feature partitions.
   - Class probability distributions blended:
     $$P(y = c | \mathbf{x}) = 0.55 \cdot P_{\text{RF}}(c | \mathbf{x}) + 0.45 \cdot P_{\text{ET}}(c | \mathbf{x})$$
   - Predicted class $\hat{y} = \arg\max_c P(y = c | \mathbf{x})$ selected from `{Normal, DoS, Probe, R2L, U2R}`.
5. **Unsupervised Anomaly Scoring (Isolation Forest)**:
   - Evaluates tree traversal path lengths: $s(\mathbf{x}, n) = 2^{-\frac{E(h(\mathbf{x}))}{c(n)}}$.
   - Normalized anomaly score percentage calculated.
   - If anomaly risk $> 55\%$, flags threat as `SUSPICIOUS_ANOMALY`.
6. **Automated Mitigation Policy**:
   - Maps severity to action: `ALLOW`, `BLOCK & THROTTLE`, `BLACKLIST SOURCE IP`, `REVOKE CREDENTIALS`, or `QUARANTINE HOST`.
7. **Transactional Persistence**:
   - Full packet telemetry, classification, anomaly metrics, and latency logged to `nids.db`.
