# System Architecture: Fruit Quality Grading & Conveyor Sorter (PROJECT-041)

## 1. System Topology Overview
AUTONOMOUS FRUIT-GRADING AI implements an agri-food cyber-physical computer vision microservice designed for high-speed optical inspection, multi-task botanical and defect classification, and neural freshness forecasting across industrial packhouse conveyor sorting lines.

```
+---------------------------------------------------------------------------------+
|                        HIGH-SPEED CONVEYOR BELT SENSING                         |
|    [Industrial Line-Scan Camera / 1080p 60 FPS]  -->  [Optical Tunnel]          |
|    - 4 Multi-Product Conveyor Lanes (Apple, Orange, Banana, Mango)              |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       PYTORCH NEURAL INFERENCE ENGINE                           |
|  +-------------------------------------+   +---------------------------------+  |
|  | MultiTaskFruitNet (Phase 2 SOTA)    |   | FruitFreshnessShelfLifeRegressor|  |
|  | - Shared 3-Stage ConvNet Backbone   |   | - 10-Feature Telemetry Trunk    |  |
|  | - Variety Head (4 Classes, 90.0%)   |   | - Multi-Head Continuous Outputs:|  |
|  | - Grade Head (3 Classes, 100.0%)    |   |   Flesh Firmness (MAE: 6.39 N), |  |
|  | - Defect Head (5 Typologies)        |   |   Sugar Brix (MAE: 1.23%),      |  |
|  | - 391 KB Ultra-Lean Serialization   |   |   Shelf Life (MAE: 2.11 Days)   |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Grade, Defect Area, Freshness Profile)
+---------------------------------------------------------------------------------+
|                  PNEUMATIC CHUTE ACTUATION & DIVERTER LOGIC                     |
|  - GRADE_A_PREMIUM  --> Bin 1 (International Export Chute)                      |
|  - GRADE_B_STANDARD --> Bin 2 (Domestic Supermarket Retail Chute)               |
|  - GRADE_C_REJECT   --> Bin 3 (Processing Juicing / Bio-Discard Chute)         |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [fruit_items] [sorting_lanes]                                                  |
|  [audit_ledger (SHA-256 Block Chaining with Genesis Seeding)]                   |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5041) & INTERACTIVE HUD                   |
|  - 60 FPS Conveyor Belt Canvas           - Grade & Freshness Analytics Charts   |
|  - 4-Lane Quick Switcher Toolbar         - Cryptographic Block Chain Explorer   |
+---------------------------------------------------------------------------------+
```
