# System Architecture: PROJECT-052 Crowd Density & Anomaly Platform

## 1. High-Level System Architecture
The AI Crowd Density Estimation and Public Safety Anomaly Detection Platform is engineered as an enterprise-grade asynchronous microservice deployed on **Port 5052**.

```
                         [CCTV Surveillance Stream / Optical Sensors]
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                           ▼
             [CSRNetCrowdDensityNet]              [CrowdOpticalFlowRiskRegressorNet]
             • VGG-16 Feature Front-End           • 12-Dimensional Telemetry Vector
             • Dilated Conv2d Back-End (r=2,2,2,4)• Multi-Task Optical Flow Regressor
             • 16x16 Density Map (350,950 params) • Risk, Turb, Correction (12,648 params)
                        │                                           │
                        └─────────────────────┬─────────────────────┘
                                              ▼
                             [Public Safety Directive Engine]
                              • Stampede Surge Detection
                              • Emergency Egress Gate Interlocks
                                              │
                                              ▼
                                [FastAPI Gateway (Port 5052)]
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                           ▼
            [SQLite WAL Mode Storage]                 [Cryptographic Audit Ledger]
            • Table: crowd_monitoring_events          • Continuous SHA-256 Hash Chain
            • 6,000 Verified Telemetry Rows           • Genesis Block #0 Seeding
```

## 2. Port Allocation
- **Assigned Port**: `5052`
- **Formula**: `5001 + 52 - 1 = 5052`
- **Transport**: HTTP/1.1 REST + WebSockets (`/api/ws`) for live alert broadcasting.

## 3. Dual PyTorch Neural Engines
1. **CSRNetCrowdDensityNet**:
   - Parameters: 350,950
   - Front-end VGG-16 feature extractor + 4 cascaded dilated convolutions (dilation rates [2, 2, 2, 4]) + 5-class anomaly head.
2. **CrowdOpticalFlowRiskRegressorNet**:
   - Parameters: 12,648
   - Multi-task dense network with BatchNorm, dropout, and 4 specialized regression/classification heads.
3. **Total Active Parameters**: 363,598 parameters.
