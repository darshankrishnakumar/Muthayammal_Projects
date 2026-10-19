# VIGILANCE-AI System Architecture & Hardware Topology

## 1. High-Level Architecture
VIGILANCE-AI is an edge-optimized In-Cabin Driver Monitoring System (DMS) engineered for commercial fleet operations. It operates as an autonomous pipeline executing optical Near-Infrared (NIR) landmark localization, deep residual neural network classification, continuous attention regression, and relational SQLite WAL auditing on **Port 5035**.

```
[In-Cabin Optical NIR Camera (30 FPS)]
                │
                ▼
[Facial Landmark Extractor (68 Points)]
                │
        ┌───────┴────────────────────────┐
        ▼                                ▼
[Eyelid Contours (36-47)]       [Lip Contours (48-67)]
   -> Eye Aspect Ratio (EAR)        -> Mouth Aspect Ratio (MAR)
        │                                │
        └───────────────┬────────────────┘
                        ▼
       [3D Head Pose Solver (PnP: Pitch, Yaw, Roll)]
       [PERCLOS 60s Window Rolling Accumulator]
                        │
                        ▼
   [Standardized 8-D Physical Telemetry Tensor]
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
[DriverFatigueClassifierNet]     [AttentionScoreRegressorNet]
  - Residual MLP (LayerNorm)       - Dual-Head Regressor
  - 4 Fatigue State Tiers          - Driver Vigilance (0-100%)
  - 97.25% Test Accuracy           - Microsleep Risk [0.0, 1.0]
       │                                 │
       └────────────────┬────────────────┘
                        ▼
   [Active Multi-Stage Safety Intervention Matrix]
     ├── Stage 0: Nominal Alert (Passive Logging)
     ├── Stage 1: Visual Advisory Notice (Vig < 80%)
     ├── Stage 2: 880Hz Acoustic Chime (Vig < 70%)
     └── Stage 3: Strobe Siren & Haptic Pulses (Critical)
                        │
                        ▼
[ACID SQLite Storage ('driver_safety.db' in WAL Mode)]
  - Driver Profiles & Shift Context
  - High-Throughput Telemetry Frames
  - Active Intervention & Acknowledgment Log
  - Cryptographic SHA-256 Audit Ledger
```

## 2. Hardware Topology & Sensor Specs
- **Sensor**: 1/2.8" CMOS Near-Infrared (NIR) global shutter camera (1280x800 resolution @ 30 FPS).
- **Illumination**: Dual 850nm NIR LED illuminators with automatic pulse width modulation.
- **Compute Unit**: NVIDIA Jetson Orin Nano (6-Core ARM Cortex-A78AE, 1024-core Ampere GPU).
- **Interface**: Automotive Ethernet & J1939 CAN-bus interface for vehicle telematics.
