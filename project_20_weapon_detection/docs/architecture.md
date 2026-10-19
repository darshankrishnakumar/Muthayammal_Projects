# VIGIL-8 System Architecture & Pipeline Topology

## 1. Executive Topology Overview
Project-020 delivers **VIGIL-8: Automated Weapon Detection & Autonomous Security Threat Interdiction Suite**, a high-assurance cyber-physical security monitoring system that bridges deep convolutional computer vision with immediate physical interlock response.

```
+-------------------------------------------------------------------------------+
|                       SECURITY COMMAND PRESENTATION TIER                      |
|   HTML5 / CSS3 Dark Glassmorphic SPA • Canvas Visual HUD Overlay • Port 5020  |
|   Console | Dual Compare | Heatmap | Radio | CCTV Wall | Model | Audit | Analytics|
+---------------------------------------+---------------------------------------+
                                        | HTTP REST API (Base64 Frames & JSON)
+---------------------------------------v---------------------------------------+
                                APPLICATION TIER                                |
|   Python 3.12 Flask Microservices • CORS Security • Camera Orchestrator       |
|   Tactical Protocol State Engine • Site Lockdown Interlock Controller         |
+---------------------------------------+---------------------------------------+
                    |                                       |
+-------------------v-------------------+       +-----------v-------------------+
|         DUAL-ENGINE VISION TIER       |       |       PERSISTENCE TIER        |
|  • Ultralytics YOLOv8n (3.0M Params)  |       |  • Relational SQLite Storage  |
|  • Modified CSPDarknet53 + PAN-FPN    |       |  • 'weapon_detection.db'      |
|  • Decoupled Anchor-Free Head (CIoU)  |       |  • incidents (JSON metrics)   |
|  • OpenCV Laplacian Variance Metric   |       |  • cctv_cameras matrix        |
|  • Canny Edge Morphology Heuristics   |       |  • threat_definitions & audit |
+---------------------------------------+       +-------------------------------+
```

## 2. Component Breakdown
- **Presentation Layer**: 9-module cyber command center with interactive canvas HUD bounding-box renderers, raw-versus-processed split comparison viewports, 2D spatial threat heatmaps, simulated radio audio dispatch, and dynamic charts.
- **Application Services**: Multithreaded Flask REST microservice deployed on Port 5020 providing `/api/detect`, `/api/samples`, `/api/incidents`, `/api/threats`, `/api/audit`, and emergency lockdown coordination.
- **Neural & Forensic Inference Engine**: Dual-engine pipeline executing real-time deep learning (YOLOv8n) with complementary computer vision edge/Laplacian telemetry for high recall under occlusion.
- **Database Layer**: SQLite transactional engine maintaining complete auditable chain-of-custody logs with cryptographic ISO timestamps.
