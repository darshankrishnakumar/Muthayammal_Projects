# System Architecture: PROJECT-053 Railway Track Defect Platform

## 1. High-Level System Architecture
The AI Railway Track Defect Detection and Structural Integrity Monitoring Platform is engineered as an enterprise-grade asynchronous microservice deployed on **Port 5053**.

```
                 [High-Speed Inspection Vehicle Vision / Bogie Sensors]
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
          [ResUNetRailDefectSegmenter]         [RailTrackGeometryAndDegradationRegressorNet]
          • Contracting ResNet Encoder         • 12-Dimensional Telemetry Vector
          • Residual Skip Connections          • Multi-Task Track Geometry Regressor
          • 6-Class Defect Mask (374,342 p)    • TQI, Speed Limit, Risk (12,582 p)
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           ▼
                          [Rail Safety Directive Engine]
                           • Automatic Speed Restrictions
                           • Urgent Maintenance Gang Dispatch
                                           │
                                           ▼
                             [FastAPI Gateway (Port 5053)]
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
         [SQLite WAL Mode Storage]                 [Cryptographic Audit Ledger]
         • Table: railway_defect_records           • Continuous SHA-256 Hash Chain
         • 6,000 Verified Telemetry Rows           • Genesis Block #0 Seeding
```

## 2. Port Allocation
- **Assigned Port**: `5053`
- **Formula**: `5001 + 53 - 1 = 5053`
- **Transport**: HTTP/1.1 REST + WebSockets (`/api/ws`) for real-time track inspection broadcasting.

## 3. Dual PyTorch Neural Engines
1. **ResUNetRailDefectSegmenter**:
   - Parameters: 374,342
   - 3-stage contracting encoder with residual skips + bridge + 2-stage expansive decoder with skip concatenations + 6-class classifier head.
2. **RailTrackGeometryAndDegradationRegressorNet**:
   - Parameters: 12,582
   - Multi-task dense network with BatchNorm, dropout, and 4 specialized regression/classification heads.
3. **Total Active Parameters**: 386,924 parameters.
