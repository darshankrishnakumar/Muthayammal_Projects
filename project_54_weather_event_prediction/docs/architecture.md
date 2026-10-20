# System Architecture: PROJECT-054 Weather Nowcasting Platform

## 1. High-Level System Architecture
The AI Weather Event Classification & Severe Storm Nowcasting Platform is engineered as an enterprise-grade asynchronous microservice deployed on **Port 5054**.

```
                 [Meteorological AWOS Stations & Doppler NEXRAD Radar]
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
          [BiGRUWeatherNowcastingNet]          [RadarPrecipitationAndExtremeWeatherRegressorNet]
          • 12-Hour Sequence Encoder           • 12-Dimensional Atmospheric Vector
          • Bidirectional Temporal Attention   • Multi-Task Thermodynamic Regressor
          • 5-Class Hazard Logits (115,270 p)  • Rain Rate, CAPE, Gusts, Risk (12,615 p)
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           ▼
                         [Civil Protection Directive Engine]
                          • Severe Convective Storm Warnings
                          • Flash Flood & Gale Interlocks
                                           │
                                           ▼
                             [FastAPI Gateway (Port 5054)]
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
         [SQLite WAL Mode Storage]                 [Cryptographic Audit Ledger]
         • Table: weather_forecast_records         • Continuous SHA-256 Hash Chain
         • 6,000 Verified Telemetry Rows           • Genesis Block #0 Seeding
```

## 2. Port Allocation
- **Assigned Port**: `5054`
- **Formula**: `5001 + 54 - 1 = 5054`
- **Transport**: HTTP/1.1 REST + WebSockets (`/api/ws`) for live severe weather alert broadcasting.

## 3. Dual PyTorch Neural Engines
1. **BiGRUWeatherNowcastingNet**:
   - Parameters: 115,270
   - 2-layer Bidirectional GRU with temporal attention pooling across 12-hour meteorological sequence horizon.
2. **RadarPrecipitationAndExtremeWeatherRegressorNet**:
   - Parameters: 12,615
   - Multi-task dense network with BatchNorm, dropout, and 5 specialized regression/classification heads.
3. **Total Active Parameters**: 127,885 parameters.
