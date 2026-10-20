# Demonstration & Walkthrough Script: AI-Based Crowd Density Estimation & Anomaly Detection (PROJECT-052)

## Overview
- **Project Identifier**: PROJECT-052
- **Module**: `project_52_crowd_density_estimation`
- **Assigned Port**: `5052`
- **Video Target Duration**: `180.000000 seconds (03:00.000)`
- **Format**: `1280x800 H.264 MP4 (720 frames @ 4.0 fps)`
- **Primary Architecture**: Dual PyTorch Networks (`CSRNetCrowdDensityNet` [350,950 params] + `CrowdOpticalFlowRiskRegressorNet` [12,648 params] = 363,598 params total)

## 6-Phase Script Sequence (30 Seconds per Phase)
1. **00:00 - 00:30 | Phase 1: Title & System Overview**
   - Live dashboard display on Port 5052 with Dual PyTorch Engines indicator and SQLite WAL badge.
   - Walk through fleet KPI cards: 6,000 Total Monitored Scans, 1,348 Active Anomaly Alerts, 218 Mean Monitored Crowd, 23.4 ms Latency.
2. **00:30 - 01:00 | Phase 2: CSRNet 16x16 Spatial Density Heatmap HUD**
   - Examine CSRNet high-resolution spatial density heatmap grid (256 color-coded intensity cells).
   - Review dilated convolution receptive field expansion and density MAE: 4.8 people vs 16.2 baseline.
3. **01:00 - 01:30 | Phase 3: Zone Telemetry 1 & 2: Central Plaza Surge & North Gate Turnstiles**
   - Execute scan on Central Plaza Concourse under high surge: 442 persons, risk score 0.88, optical turbulence 0.82, Dangerous Congestion alert.
   - Execute scan on North Gate Turnstiles: venue bottleneck queuing pressure and automated turnstile throughput advisory.
4. **01:30 - 02:00 | Phase 4: Zone Telemetry 3 & 4: Transit Station Platform & Stadium Exit Corridor**
   - Execute scan on Transit Station Platform 2: 215 persons, normal flow dynamics, perimeter monitoring.
   - Execute scan on Stadium Emergency Exit Corridor under high influx: Stampede Surge trigger, activating emergency concourse drain.
5. **02:00 - 02:30 | Phase 5: Live Crowd Telemetry Log & SQLite WAL Persistence**
   - Scroll through the 6,000-record crowd security log in `crowd_monitoring_events`.
   - Inspect relational schema, zero-null integrity, and instant ACID query performance.
6. **02:30 - 03:00 | Phase 6: Cryptographic Audit Ledger & Continuous Hash Chaining**
   - Verify Genesis Block #0 with 64-character deterministic zero-hash predecessor.
   - Demonstrate continuous SHA-256 block hash chaining and tamper-evident audit logging for municipal safety compliance.
