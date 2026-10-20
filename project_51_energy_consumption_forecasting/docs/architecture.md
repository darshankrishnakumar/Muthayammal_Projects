# System Architecture: PROJECT-051 Smart Energy Forecasting Platform

## 1. High-Level System Architecture
The Smart Energy Consumption Forecasting and Dynamic Peak Shaving Platform is engineered as an enterprise-grade asynchronous microservice deployed on **Port 5051**.

```
                         [Facility Telemetry & Environmental Sensors]
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                           ▼
            [MultiHorizonEnergyLSTM]              [GridPeakAndCarbonEmissionRegressorNet]
            • 2-Layer Bi-LSTM (hidden=64)         • 12-Dimensional Telemetry Vector
            • 24-Hour Hourly Load Trajectory      • Multi-Task Grid Impact Regressor
            • Linear Projection (145,496 params)  • Shaving, Cost, CO2, Stress (12,613 params)
                        │                                           │
                        └─────────────────────┬─────────────────────┘
                                              ▼
                             [Constrained Peak Shaving Engine]
                              • Peak Capping: P_opt = P_peak * (1 - shave_pct)
                              • Energy Shifted to Off-Peak: [0-5, 22-23]
                                              │
                                              ▼
                                [FastAPI Gateway (Port 5051)]
                                              │
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                           ▼
            [SQLite WAL Mode Storage]                 [Cryptographic Audit Ledger]
            • Table: energy_plans                     • Continuous SHA-256 Hash Chain
            • 6,000 Verified Telemetry Rows           • Genesis Block #0 Seeding
```

## 2. Port Allocation
- **Assigned Port**: `5051`
- **Formula**: `5001 + 51 - 1 = 5051`
- **Transport**: HTTP/1.1 REST + Chart.js dynamic dashboard.

## 3. Dual PyTorch Neural Engines
1. **MultiHorizonEnergyLSTM**:
   - Parameters: 145,496
   - 2-layer Bidirectional LSTM (hidden_dim=64, dropout=0.2) + MLP projection head to 24 hourly load outputs.
2. **GridPeakAndCarbonEmissionRegressorNet**:
   - Parameters: 12,613
   - Multi-task dense network with BatchNorm, dropout, and 4 specialized regression heads.
3. **Total Active Parameters**: 158,109 parameters.
