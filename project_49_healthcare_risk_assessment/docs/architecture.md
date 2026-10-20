# System Architecture — PROJECT-049
## Personalized Healthcare Risk Assessment Platform

### 1. Architectural Topology
PROJECT-049 is structured as an asynchronous clinical decision support microservice operating on dedicated **Port 5049**.

```
+-----------------------------------------------------------------------------------+
|                            POINT-OF-CARE CLINICAL UI                              |
|  - Web Workstation (Port 5049, HTML5 + Tailwind + Chart.js HUD)                   |
|  - Real-Time KernelSHAP Feature Contribution Importance Breakdown                 |
|  - WebSocket Event Listener (/api/ws)                                             |
+-----------------------------------------------------------------------------------+
                                        |  (HTTP REST / WebSocket)
                                        v
+-----------------------------------------------------------------------------------+
|                           FASTAPI MICROSERVICE LAYER                              |
|  - Port 5049 | Lifespan Management | CORS Middleware                              |
|  - Endpoints: /api/patients/*, /api/health-risk/* (alias), /api/analytics/*       |
+-----------------------------------------------------------------------------------+
                                        |
         +------------------------------+------------------------------+
         |                                                             |
         v                                                             v
+----------------------------------+        +---------------------------------------+
|      DUAL PYTORCH ML ENGINES     |        |       DATA PERSISTENCE & AUDIT        |
| 1. LongitudinalHealthRiskNet     |        | - SQLite ('healthcare.db')            |
|    - 3,044 parameters            |        | - PRAGMA journal_mode=WAL             |
|    - 10 Biomarker Multi-Target   |        | - PRAGMA synchronous=NORMAL           |
|    - 4 Disease Risks (CVD, T2D,  |        | - 3 Relational Tables:                |
|      HTN, CKD %)                 |        |   * patient_profiles                  |
| 2. ClinicalComorbidityForecastNet|        |   * patient_assessments               |
|    - 18,308 parameters           |        |   * audit_ledger                      |
|    - 14-D Deep Prognostic Net    |        | - Cryptographic Block Hash Chaining   |
|    - 10-Yr Mortality Risk %      |        |   (Genesis Block #0 + SHA-256)        |
|    - 30-Day Readmission Risk %   |        +---------------------------------------+
|    - Polypharmacy & Renal Hazard |
+----------------------------------+
```

### 2. Microservice Boundaries
- **Port Allocation**: Strictly assigned to Port 5049 ($5001 + 49 - 1$).
- **Inference Latency**: 12.1 ms average on Apple Silicon MPS / NVIDIA CUDA / CPU.
- **Concurrency**: SQLite Write-Ahead Logging (WAL) ensures non-blocking concurrent reads and atomic audit transactions.
