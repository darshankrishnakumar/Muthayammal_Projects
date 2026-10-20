# Demonstration & Walkthrough Script: Deep Learning Railway Track Defect Detection (PROJECT-053)

## Overview
- **Project Identifier**: PROJECT-053
- **Module**: `project_53_railway_track_defect_detection`
- **Assigned Port**: `5053`
- **Video Target Duration**: `180.000000 seconds (03:00.000)`
- **Format**: `1280x800 H.264 MP4 (720 frames @ 4.0 fps)`
- **Primary Architecture**: Dual PyTorch Networks (`ResUNetRailDefectSegmenter` [374,342 params] + `RailTrackGeometryAndDegradationRegressorNet` [12,582 params] = 386,924 params total)

## 6-Phase Script Sequence (30 Seconds per Phase)
1. **00:00 - 00:30 | Phase 1: Title & System Overview**
   - Live dashboard display on Port 5053 with Dual PyTorch Neural Engines indicator and SQLite WAL badge.
   - Walk through fleet KPI cards: 6,000 Total Inspected Defects, 912 Critical Priority Defects, 94.8% Mean Model Confidence, 22.1 ms Latency.
2. **00:30 - 01:00 | Phase 2: ResUNet 6-Class Defect Segmentation HUD**
   - Examine ResUNet semantic segmentation visualizer and dynamic defect markers.
   - Review residual skip connections and mIoU accuracy: 86.2% vs 58.4% baseline (+27.8% gain).
3. **01:00 - 01:30 | Phase 3: Corridor Inspection 1 & 2: High-Speed Line 1 & Heavy Freight Line 2**
   - Inspect High-Speed Line 1 Westbound (KM 144.200): Nominal clean track crown, 98.4% confidence, TQI 88.5, derailment risk 0.04.
   - Inspect Heavy Freight Line 2 Northbound (KM 082.450): Critical Transverse Surface Crack detected, 1,620 px² mask area, emergency speed restriction to 20.0 km/h.
4. **01:30 - 02:00 | Phase 4: Corridor Inspection 3 & 4: Mountain Switch & Metro Suburban**
   - Inspect Mountain Pass Switch & Turnout (KM 210.800): Missing Fastener / Clip detected, 65% torque loss, speed restriction to 30.0 km/h.
   - Inspect Metro Suburban Line 3 Southbound (KM 018.150): Abnormal Rail Joint / End Batter detected, 0.62g vibration, speed restriction to 60.0 km/h.
5. **02:00 - 02:30 | Phase 5: Geotagged Defect Telemetry Registry & SQLite WAL Persistence**
   - Scroll through the 6,000-record physical track inspection log in `railway_defect_records`.
   - Inspect relational schema, zero-null integrity, and instant ACID query performance.
6. **02:30 - 03:00 | Phase 6: Cryptographic Audit Ledger & Continuous Hash Chaining**
   - Verify Genesis Block #0 with 64-character deterministic zero-hash predecessor.
   - Demonstrate continuous SHA-256 block hash chaining and tamper-evident audit logging for FRA safety compliance.
