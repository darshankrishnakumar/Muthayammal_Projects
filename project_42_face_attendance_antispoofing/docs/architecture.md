# System Architecture: Face Recognition Attendance & Anti-Spoofing (PROJECT-042)

## 1. System Topology Overview
The AI-Driven Face Recognition Attendance & Anti-Spoofing Platform is an enterprise cyber-physical microservice architecture engineered for high-throughput pedestrian turnstile gateways, continuous presentation attack forensics, and immutable cryptographic record-keeping.

```
+---------------------------------------------------------------------------------+
|                        BIOMETRIC OPTICAL TURNSTILE SENSING                      |
|    [Industrial Near-IR / RGB Global Shutter Camera]  -->  [Turnstile Gateway]   |
|    - Micro-saccadic eye tracking, facial oval alignment, pupil IOD scale       |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       PYTORCH DUAL NEURAL INFERENCE ENGINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | DeepAntiSpoofFaceNet (ArcFace Core) |   | BiometricLivenessQualityNet     |  |
|  | - 512-D Spherical Hypersphere Embed |   | - 10-Feature Telemetry Trunk    |  |
|  | - Additive Angular Margin m=0.50    |   | - Multi-Head Continuous Outputs:|  |
|  | - Binary Spoof Classifier (100.0%)  |   |   Spoof Risk % (MAE: 2.35%),    |  |
|  | - 1.57 MB Serialized PyTorch Model  |   |   Micro-Tremor (MAE: 0.046),    |  |
|  | - Cosine Distance Tau = 0.68        |   |   Illum Entropy (MAE: 0.58 pts) |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Identity Match, Liveness Status, Spoof Risk)
+---------------------------------------------------------------------------------+
|                     TURNSTILE MOTOR CONTROLLER & RELAYS                         |
|  - STATUS: PRESENT        --> 5V Dry-Contact Relay Pulse (Turnstile Unlocks)    |
|  - STATUS: REJECTED_SPOOF --> Turnstile Locked (Warning Buzzer, Security Alert) |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [students] [attendance_records]                                                |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5042) & INTERACTIVE HUD                   |
|  - 60 FPS Face Mesh Canvas               - Real-Time Liveness Telemetry Chart   |
|  - Student Profile Switcher              - Cryptographic Block Chain Explorer   |
+---------------------------------------------------------------------------------+
```
