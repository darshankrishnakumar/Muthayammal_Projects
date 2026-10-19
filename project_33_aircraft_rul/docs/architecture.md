# System Architecture: AERO-RUL (PROJECT-033)

## 1. High-Level System Overview
AERO-RUL is an enterprise-grade Aerospace Prognostics and Health Management (PHM) system designed to monitor and predict the Remaining Useful Life (RUL) of mission-critical commercial aircraft turbofan engines. The system couples multi-channel aerodynamic and thermodynamic sensor telemetry with dual deep neural network architectures.

```
+-----------------------------------------------------------------------------------+
|                        COMMERCIAL AIRCRAFT TURBOFAN FLEET                         |
|   CFM56-7B / LEAP-1B | GE90-115B | Trent 1000 | PW1100G-JM | CF34-8E              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         FADEC AIRBORNE TELEMETRY STREAM                           |
|   T50 LPT Temp | P30 HPC Pressure | Nc Core Speed | Nf Fan Speed | EGT Margin ... |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    PYTHON / FLASK REST MICROSERVICE (PORT 5033)                   |
|                                                                                   |
|  +-------------------------------------+   +------------------------------------+  |
|  |  AviationAirworthinessClassifierNet |   |     TurbofanRULRegressorNet        |  |
|  |  Deep Residual MLP (BatchNorm/GELU) |   |  Dual-Head LayerNorm MLP           |  |
|  |  Accuracy: 98.08% | 3 Classes       |   |  Health Score & RUL Flight Cycles  |  |
|  +-------------------------------------+   +------------------------------------+  |
|                                         |                                         |
|  +-------------------------------------+   +------------------------------------+  |
|  |  Relational SQLite (WAL Mode)       |   |  Aerospace Telemetry HUD           |  |
|  |  5 Schemas + Immutable Audit Trail  |   |  Chart.js Degradation Decay Splines|  |
|  +-------------------------------------+   +------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 2. Component Subsystems
1. **High-Pressure Turbine (HPT) Blades**: CFM56-7B / LEAP-1B (4,200 max cycles). Thermal creep and oxidation.
2. **High-Pressure Compressor (HPC) Rotor**: GE90-115B (6,000 max cycles). High-cycle fatigue micro-cracking.
3. **Mainshaft Roller Bearings (#4 Bearing)**: Trent 1000 (5,500 max cycles). Subsurface shear fatigue and outer race spallation.
4. **Fuel Metering Unit (FMU)**: PW1100G-JM (8,500 max cycles). Servo-valve sticking and orifice cavitation.
5. **Low-Pressure Turbine (LPT) Stator**: CF34-8E (7,200 max cycles). Ceramic Thermal Barrier Coating (TBC) delamination.

## 3. Data Persistence Layer
- SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
- 5 Relational Schemas: `aircraft_components`, `flight_telemetry`, `rul_predictions`, `maintenance_shop_orders`, `audit_log`.
