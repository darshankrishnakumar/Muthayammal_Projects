# Project 32: System Architecture

```
+-----------------------------------------------------------------------------------+
|                        INDUSTRIAL ASSET SENSOR TELEMETRY                          |
|   [Accelerometers]   [RTD Thermal]   [Pressure Transducers]   [Encoders]   [AE]   |
+------------------------------------------+----------------------------------------+
                                           | 8-D Multivariate Stream (Vib/Temp/Press)
                                           v
+-----------------------------------------------------------------------------------+
|                     APPLICATION TIER (Flask Microservice @ Port 5032)             |
|  +-----------------------------------------------------------------------------+  |
|  | REST Endpoints: /api/analyze, /api/machines, /api/history, /api/work-order  |  |
|  +-----------------------------------------------------------------------------+  |
|                                          |                                        |
|         +--------------------------------+-------------------------------+        |
|         v                                                                v        |
|  +----------------------------------+          +-------------------------------+  |
|  | MachineHealthClassifierNet       |          | RULRegressorNet               |  |
|  | - Deep Residual MLP              |          | - LayerNorm + GELU MLP        |  |
|  | - 6 Fault Classes Diagnosis      |          | - Health Score (0-100)        |  |
|  | - Cross-Entropy Loss             |          | - RUL Hours (24 - 4,000 hrs)  |  |
|  +----------------------------------+          +-------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     DATA PERSISTENCE & WORK ORDER DISPATCH TIER                   |
|  +-----------------------------------------------------------------------------+  |
|  | SQLite Relational DB (predictive_maintenance.db) in WAL Mode                |  |
|  | Tables: machines, sensor_telemetry, diagnostic_inspections, work_orders     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
