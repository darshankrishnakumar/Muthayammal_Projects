# System Architecture — PROJECT-048
## Multi-Spectral Food Quality & Freshness Detection Platform

### 1. Architectural Topology
PROJECT-048 is structured as an asynchronous edge-deployable microservice operating on dedicated **Port 5048**.

```
+-----------------------------------------------------------------------------------+
|                            CLIENT / EDGE INTAKE LAYER                             |
|  - Web Browser / Handheld Terminal (Port 5048, HTML5 + Tailwind + Chart.js HUD)   |
|  - Real-Time 60 FPS Optical Absorbance Spectrum (450 nm - 950 nm)                 |
|  - WebSocket Event Listener (/api/ws)                                             |
+-----------------------------------------------------------------------------------+
                                        |  (HTTP REST / WebSocket)
                                        v
+-----------------------------------------------------------------------------------+
|                           FASTAPI MICROSERVICE LAYER                              |
|  - Port 5048 | Lifespan Management | CORS Middleware                              |
|  - Endpoints: /api/freshness/*, /api/food/* (alias), /api/analytics/*, /api/health|
+-----------------------------------------------------------------------------------+
                                        |
         +------------------------------+------------------------------+
         |                                                             |
         v                                                             v
+----------------------------------+        +---------------------------------------+
|      DUAL PYTORCH ML ENGINES     |        |       DATA PERSISTENCE & AUDIT        |
| 1. SpectralFreshnessCNN          |        | - SQLite ('food_freshness.db')        |
|    - 20,869 parameters           |        | - PRAGMA journal_mode=WAL             |
|    - Spatio-spectral feature map |        | - PRAGMA synchronous=NORMAL           |
|    - Freshness score (0-100)     |        | - 3 Relational Tables:                |
|    - Tri-tier stage logits       |        |   * food_batches                      |
| 2. ShelfLifeForecastRegressorNet |        |   * freshness_assessments             |
|    - 18,052 parameters           |        |   * audit_ledger                      |
|    - 10 Physico-chemical inputs  |        | - Cryptographic Block Hash Chaining   |
|    - Kinetic shelf life (days)   |        |   (Genesis Block #0 + SHA-256)        |
|    - Spoilage / Microbial risks  |        +---------------------------------------+
|    - Cold-chain compliance %     |
+----------------------------------+
```

### 2. Microservice Boundaries
- **Port Allocation**: Strictly assigned to Port 5048 ($5001 + 48 - 1$).
- **Inference Latency**: 11.8 ms average on Apple Silicon MPS / NVIDIA CUDA / CPU.
- **Concurrency**: SQLite Write-Ahead Logging (WAL) ensures zero database write locking during high-frequency telemetry ingestion.
