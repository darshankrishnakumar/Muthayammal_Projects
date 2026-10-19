# Walkthrough Timestamps: AERO-RUL (PROJECT-033)

**Application Title**: Aircraft Component Remaining Useful Life (RUL) Prediction Using Machine Learning & NASA C-MAPSS Telemetry  
**Port**: 5033 (`http://127.0.0.1:5033/`)  
**Duration**: Exactly 180.000 seconds (03:00)  
**Video File**: `walkthrough/walkthrough_video.mp4` (H.264, 1280x800, 24fps)

---

| Timestamp | Phase | Topic / Demonstration Point | Technical Details |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | Fleet Overview & Telemetry Metrics Strip | Overview of commercial turbofan fleet status, 94.2% fleet health index, AOG count, FAA compliance rate, and microservice health on Port 5033. |
| **00:30 - 01:00** | Phase 2 | Subsystem Selection & C-MAPSS Sensor Array | Interactive selection of High-Pressure Compressor (HPC) Rotor (GE90-115B) and inspection of 6 C-MAPSS sensor gauges (T50, P30, Nc, Nf, EGT margin, cycles). |
| **01:00 - 01:30** | Phase 3 | Weibull Degradation Spline & Sensor Deviations | Real-time 11-point degradation decay curve visualization against the 30% red dashed critical safety threshold, alongside sensor deviation bar charts. |
| **01:30 - 02:00** | Phase 4 | Critical Wear Simulation & AOG Grounding | Simulation of high flight cycle stress (90% wear) on Mainshaft Roller Bearings, triggering immediate GROUNDED / MANDATORY SHOP VISIT and visual alarm. |
| **01:20 - 02:30** | Phase 5 | Maintenance Shop Orders (MSO) Dispatch | Inspection of active shop orders (MSO-2026-081) for engine teardown, eddy-current non-destructive testing, and creation of new work orders. |
| **02:30 - 03:00** | Phase 6 | FAA / EASA Audit Trail & SQLite WAL Ledger | Immutable audit logging of all inference decisions and maintenance dispatches with ISO-8601 UTC timestamps stored in SQLite WAL mode. |
