# Walkthrough Timestamps: PREDICTIVE MAINTENANCE OF INDUSTRIAL MACHINES (PROJECT-032)

Exact Target Video Duration: **180.000 Seconds (03:00.00)**  
Video Specifications: **1280x800 H.264 MP4 @ 24fps Constant Framerate**

| Timestamp Range | Phase | Phase Description & Operational Demonstration |
|---|---|---|
| **00:00 - 00:30** | Phase 1 | **System Overview & Industrial Fleet Telemetry Strip**: Live metric strip inspection (Fleet Health Index 92%, Critical Urgencies, Connected Assets, 99.92% Uptime SLA), `/api/health` verification on Port 5032, asset carousel across 5 industrial rotating machines. |
| **00:30 - 01:00** | Phase 2 | **Asset Selection & 8-Band FFT Vibration Spectrum**: Interactive selection of Screw Compressor A-101 and Gas Turbine Generator D-401, live Chart.js FFT vibration spectrum breakdown (1X RPM fundamental, 2X/3X harmonics, BPFO/BPFI defect bands). |
| **00:30 - 01:00** | Phase 3 | **Multivariate Health Profile Radar Analysis**: Multi-dimensional diagnostic radar evaluation across 5 kinematic axes: Bearing Kinematics, Thermal State, Hydraulic Balance, Lubrication Quality, and Mechanical Alignment. |
| **01:30 - 02:00** | Phase 4 | **Severe Bearing Spall Inception & Immediate Alert Trigger**: PyTorch forward inference on Gas Turbine Generator D-401 triggering Outer Race Bearing Spall, vibration surge (5.8 mm/s), health score drop to 42.5%, and IMMEDIATE red urgency highlight. |
| **02:00 - 02:30** | Phase 5 | **Remaining Useful Life (RUL) & Work Order Dispatch**: Neural RUL estimation yielding 144 operating hours (6.0 Days) before catastrophic failure, automated `/api/work-order` dispatch, technician assignment, and corrective action protocol. |
| **02:30 - 03:00** | Phase 6 | **Historical Degradation Ledger & SQLite WAL Persistence**: Chronological asset maintenance inspection log inspection, ACID persistence verification, SQLite Write-Ahead Logging integrity, and 31/31 QA automated test suite conformance. |
