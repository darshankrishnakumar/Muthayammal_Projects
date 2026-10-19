# Project 31: System Architecture

```
+-----------------------------------------------------------------------------------+
|                        HYDROLOGICAL CATCHMENT SENSOR LAYER                        |
|   [Rainfall Gauges]   [Ultrasonic River Sensors]   [Soil Moisture TDR]   [DEM]    |
+------------------------------------------+----------------------------------------+
                                           | 8-D Hydro Telemetry Stream
                                           v
+-----------------------------------------------------------------------------------+
|                     APPLICATION TIER (Flask Microservice @ Port 5031)             |
|  +-----------------------------------------------------------------------------+  |
|  | REST Endpoints: /api/predict, /api/zones, /api/history, /api/dispatch       |  |
|  +-----------------------------------------------------------------------------+  |
|                                          |                                        |
|         +--------------------------------+-------------------------------+        |
|         v                                                                v        |
|  +----------------------------------+          +-------------------------------+  |
|  | FloodRiskClassifierNet           |          | InundationDepthRegressorNet   |  |
|  | - Deep Residual MLP              |          | - LayerNorm + GELU MLP        |  |
|  | - 4 Severity Alert Levels        |          | - Inundation Depth (m)        |  |
|  | - Softmax Cross-Entropy Loss     |          | - Evacuation Lead Time (hrs)  |  |
|  +----------------------------------+          +-------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                       DATA PERSISTENCE & COMMAND DISPATCH TIER                    |
|  +-----------------------------------------------------------------------------+  |
|  | SQLite Relational DB (flood_risk.db) in WAL Mode (Non-blocking concurrency) |  |
|  | Tables: river_basins, hydrological_readings, flood_predictions, audit_log   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
