# System Architecture: Automated Product Defect Detection & Quality Control (PROJECT-046)

## 1. System Topology Overview
PROJECT-046 implements an enterprise cyber-physical quality control microservice combining multi-scale computer vision, neural surface roughness regression, deterministic pneumatic actuation, and cryptographic SHA-256 data provenance.

```
+---------------------------------------------------------------------------------+
|                        HIGH-SPEED OPTICAL INGESTION                             |
|    [Line-Scan / Telecentric Cameras, 4096x3072 @ 120fps, Optical Encoders]      |
|    - Monitored Assembly Lines: SMT PCB, CNC Gear, Casing Foundry, Aerospace     |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                     DUAL-ENGINE PYTORCH INFERENCE PIPELINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | DeepFPNDefectNet                    |   | DefectRiskRegressorNet          |  |
|  | - Bottom-Up Trunk (C1-C3, 128 chan) |   | - 10-Feature Normalized Trunk   |  |
|  | - Lateral FPN Fusion (P2-P5)        |   | - 4 Multi-Target Output Heads:  |  |
|  | - 3x3 Anti-Aliasing Smoothing       |   |   Severity Score % (MAE: 0.48%) |  |
|  | - Dual Prediction Heads:            |   |   Defect Area % (MAE: 0.17%)    |  |
|  |   * Spatial Seg Map (mIoU: 93.5%)   |   |   Roughness Ra (MAE: 0.13 um)   |  |
|  |   * 5-Class Logits (F1: 96.8%)      |   |   Eject Conf % (MAE: 0.30%)     |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Verdicts, Continuous Risk, Roughness, Eject Conf)
+---------------------------------------------------------------------------------+
|                     CYBER-PHYSICAL ACTUATOR DISPATCH                            |
|  - QA Verdict: PASS   --> ROUTE_CONVEYOR (Accepted to Assembly Bin A)           |
|  - QA Verdict: REJECT --> TRIGGER_PNEUMATIC_EJECT (Pneumatic Blast to Bin B)    |
|  - Fast-Acting Solenoids (24V DC, 6.0 - 9.0 Bar Air Pulse, sub-2ms response)   |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [inspected_parts] [inspection_templates]                                       |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API & 60 FPS WEBSOCKET TELEMETRY (PORT 5046)                 |
|  - Asynchronous FastAPI Service | Dual Decorators | Thread-Safe WAL Operations  |
|  - HTML5 Canvas Laser Scanning HUD, Bounding Box Visualizer, Audit Inspector   |
+---------------------------------------------------------------------------------+
```
