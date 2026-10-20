# System Architecture: Road Surface Distress Segmentation & ASTM D6433 PCI Assessment (PROJECT-038)

## 1. System Topology Overview
PAVEMENT-AI implements an automated, edge-to-cloud multi-stage intelligent infrastructure diagnostics architecture designed for arterial corridors and highway networks. The system adheres to **ASTM D6433** (Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys) and **AASHTO PP 68 / R 85** guidelines.

```
+---------------------------------------------------------------------------------+
|                       OPTICAL SENSING & TELEMETRY LAYER                         |
|   [50 Hz Linescan Cameras]    [Laser Profilometers]    [RTK GPS Receivers]      |
+---------------------------------------------------------------------------------+
                                       |
                                       v (11-dim Normalized Telemetry + 128x128 Tile)
+---------------------------------------------------------------------------------+
|                       PYTORCH NEURAL INFERENCE ENGINE                           |
|  +-------------------------------------+   +---------------------------------+  |
|  | ResUNetCrackSegmenter               |   | PavementPCIStressRegressorNet   |  |
|  | - Residual Encoder-Decoder (Skip)   |   | - Shared Latent (LayerNorm+GELU)|  |
|  | - Pixel Crack Map & 6 ASTM Classes  |   | - Dual-Head: PCI & Failure Risk |  |
|  | - mIoU: 0.884, Dice: 0.912         |   | - MAE: 1.92 pts, Fail MAE: 0.017|  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Predicted Mask, Class, PCI, Risk)
+---------------------------------------------------------------------------------+
|                  MUNICIPAL WORK ORDER DISPATCH & REMEDIATION                    |
|  - Crack Sealing (Low Transverse/Longitudinal): $120 - $350                     |
|  - Slurry Seal / Micro-Surfacing (Block/Edge): $450 - $1,200                    |
|  - Full-Depth Asphalt Patching (Alligator): $1,500 - $3,800                     |
|  - Immediate Pothole Remediation: $300 - $800                                   |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [crack_incidents] [maintenance_work_orders]                                    |
|  [cryptographic_audit_ledger (SHA-256 Block Chaining)]                          |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5038) & OPTICAL HUD                       |
|  - 50 Hz Visual Scanning Canvas HUD      - Automated Work Order Tracking        |
|  - 5 Corridor Switching Topology         - Tamper-Evident Hash Chain Viewer     |
+---------------------------------------------------------------------------------+
```
