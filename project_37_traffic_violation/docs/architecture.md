# System Architecture: AI Traffic Violation Detection & ANPR Safety Enforcement (PROJECT-037)

## 1. System Topology Overview
TRAFFIC-AI implements a real-time, edge-to-cloud multi-stage intelligent transportation enforcement architecture designed for urban and highway corridors. The system adheres to **Indian Roads Congress (IRC) SP:90** and **ISO 39001** standards for automated electronic enforcement.

```
+---------------------------------------------------------------------------------+
|                         EDGE SENSING & TELEMETRY LAYER                          |
|  [4K UHD CCTV Cameras]  [Radar Velocity Profilers]  [Optical Signal Indicators]  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (13-dim Normalized Feature Vector)
+---------------------------------------------------------------------------------+
|                       PYTORCH NEURAL INFERENCE ENGINE                           |
|  +-------------------------------------+   +---------------------------------+  |
|  | TrafficViolationClassifierNet (MLP) |   | TrafficSafetySeverityRegressorNet|  |
|  | - 2 Residual Blocks (Skip Conn)     |   | - Shared Latent (LayerNorm+GELU)|  |
|  | - 8 Statutory Classes (100% Acc)    |   | - Dual-Head: Severity & Risk    |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Predicted Class, Severity, Risk)
+---------------------------------------------------------------------------------+
|                     MVA 2019 E-CHALLAN & STATUTORY FINES                        |
|  - Speeding (MVA Sec 183(1)): ₹2,000      - Red Light (MVA Sec 184): ₹1,000    |
|  - Wrong Way (MVA Sec 184(c)): ₹5,000    - No Helmet (MVA Sec 194D): ₹1,000  |
|  - Phone Usage (MVA Sec 184(c)): ₹1,500  - Seatbelt (MVA Sec 194B): ₹1,000    |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [intersections] [cameras] [detected_vehicles] [violations] [e_challans]        |
|  [cryptographic_audit_ledger (SHA-256 Block Chaining)]                          |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5037) & 4K CCTV HUD                       |
|  - Interactive Scenario Injection        - Real-Time e-Challan Feed             |
|  - 4 Intersections Topology Switcher     - Tamper-Evident Hash Chain Viewer     |
+---------------------------------------------------------------------------------+
```
