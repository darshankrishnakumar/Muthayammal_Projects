# 01 — System Overview & Architecture

## Executive Abstract
**PROJECT-055** is an enterprise-grade AI-Based Accident Detection and Emergency Alert System engineered to eliminate the critical notification latency gap in traumatic vehicular collisions. Operating on dedicated **Port 5055**, the system ingests live optical video streams and telemetry feeds across intelligent transportation corridors, executing sub-second accident classification, real-time physical crash severity regression, automated 911 Computer-Aided Dispatch (CAD) alert generation, and tamper-proof cryptographic audit chaining.

## Microservice Architecture
```
+-------------------------------------------------------------------------------------------------+
|                                 PROJECT 55 ENTERPRISE PLATFORM                                  |
|                                     Assigned Port: 5055                                         |
+-------------------------------------------------------------------------------------------------+
                                                  |
                     +----------------------------+----------------------------+
                     |                                                         |
                     v                                                         v
         [ Fast-Path Edge Ingest ]                                [ Computer Vision Ingest ]
        12D Kinematic Impact Vector                               16-Frame Optical Sequences
     (Decel, Yaw, Trajectory, Force)                          (Roadside CCTV / RTSP Cameras)
                     |                                                         |
                     +----------------------------+----------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |         DUAL PYTORCH ENGINES          |
                              |       198,638 Total Parameters        |
                              +---------------------------------------+
                              | Model 1: MultiCueTemporalFusionModel  |
                              |   - Spatial CNN (Conv2d x 3)          |
                              |   - Bidirectional GRU (Hidden=64)     |
                              |   - Multi-Head Cross-Attention (x4)   |
                              |   - Dynamic Attribution Gating        |
                              |                                       |
                              | Model 2: CrashSeverityNeuralNet       |
                              |   - Dense Deep Multi-Task Trunk       |
                              |   - Heads: Severity, Delta-V, Risk,   |
                              |            Required Units, Priority   |
                              +---------------------------------------+
                                                  |
                     +----------------------------+----------------------------+
                     |                                                         |
                     v                                                         v
        [ Automated CAD 911 Alert ]                               [ Cryptographic Audit Engine ]
      Level-1 Trauma Webhook Dispatch                            Continuous SHA-256 Block Chaining
      ETA, Severity, Apparatus Payload                           Genesis Block #0 -> 6,001 Blocks
                     |                                                         |
                     +----------------------------+----------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |      SQLITE WRITE-AHEAD LOGGING       |
                              |          ('data/project55_enterprise.db')         |
                              |   - 4 Roadside Cameras                |
                              |   - 6,000 Verified Telemetry Records  |
                              |   - 1,195 CAD Dispatch Records        |
                              |   - 6,001 Immutable Chained Blocks    |
                              +---------------------------------------+
```

## Core Subsystems
1. **Asynchronous REST & WebSocket Server (`FastAPI`)**: High-concurrency async event broker serving real-time telemetry on Port 5055.
2. **Deep Learning Inference Core (`PyTorch`)**: Dual neural networks executing in under 11.2ms on Apple Silicon MPS hardware.
3. **Relational ACID Storage Engine (`SQLite WAL`)**: Zero-lock concurrent reader/writer database configuration with continuous block hash verification.
4. **Interactive Command Dashboard (`Tailwind CSS + Chart.js`)**: Real-time traffic incident simulator, dynamic cue weights visualization, and incident registry.
