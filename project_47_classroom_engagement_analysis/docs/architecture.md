# System Architecture: Multimodal Classroom Engagement Analytics (PROJECT-047)

## 1. System Topology Overview
PROJECT-047 implements an edge AI microservice architecture combining multimodal perceptual feature extraction, dual PyTorch neural networks, adaptive pedagogical directives, and cryptographic SHA-256 data provenance.

```
+---------------------------------------------------------------------------------+
|                        CLASSROOM OPTICAL PERCEPTION                             |
|    [Wide-Angle PTZ Cameras, 1080p @ 60 FPS, Edge Landmark Processing]          |
|    - Courses: CS-301, MATH-210, AI-405, BIO-108 | Zero Raw Video Retention     |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                     DUAL-ENGINE PYTORCH INFERENCE PIPELINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | MultimodalEngagementNet             |   | AttentionForecastRegressorNet   |  |
|  | - 12-D Multimodal Feature Vector    |   | - 10-Feature Normalized Trunk   |  |
|  |   * 5-D Facial Action Units         |   | - 4 Multi-Target Output Heads:  |  |
|  |   * 3-D Head Pose (Yaw, Pitch, Roll)|   |   Attention Score % (MAE: 0.39%)|  |
|  |   * 4-D Posture Kinematics          |   |   Drowsiness Risk % (MAE: 3.20%)|  |
|  | - Dual Prediction Heads:            |   |   Teacher Urgency % (MAE: 4.69%)|  |
|  |   * Mean Engagement (MAE: 4.22%)    |   |   Participation Rate (MAE: 5.0%)|  |
|  |   * Action Accuracy: 100.0%         |   |                                 |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Directives, Attention Forecast, Drowsiness Risk)
+---------------------------------------------------------------------------------+
|                      AMBIENT PEDAGOGICAL INTERVENTION                           |
|  - Directive: MAINTAIN_CURRENT_PACE     --> Pacing Validated (Emerald HUD)      |
|  - Directive: ASK_CHECKPOINT_QUESTION   --> Conceptual Diagnostic (Cyan HUD)    |
|  - Directive: TRIGGER_INTERACTIVE_POLL  --> Re-engage Disengaged (Amber HUD)    |
|  - Directive: TAKE_2_MIN_REFRESHER_BREAK--> Combat Fatigue / Slump (Rose HUD)   |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [classroom_sessions] [engagement_snapshots]                                    |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API & 60 FPS WEBSOCKET TELEMETRY (PORT 5047)                 |
|  - Asynchronous FastAPI Service | Dual Decorators | Thread-Safe WAL Operations  |
|  - HTML5 Canvas Gaze HUD, Pupil Tracker, AU45 Blink Counter, Audit Inspector   |
+---------------------------------------------------------------------------------+
```
