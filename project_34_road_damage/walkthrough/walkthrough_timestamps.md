# Walkthrough Timestamps: ROAD-AI (PROJECT-034)

**Application Title**: AI-Based Road Damage Detection and Severity Classification Using YOLO & Deep Learning  
**Port**: 5034 (`http://127.0.0.1:5034/`)  
**Duration**: Exactly 180.000 seconds (03:00)  
**Video File**: `walkthrough/walkthrough_video.mp4` (H.264, 1280x800, 24fps)

---

| Timestamp | Phase | Topic / Demonstration Point | Technical Details |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | Municipal Highway Survey Overview | Overview of road asset management dashboard, total defects catalogued, mean PCI score, and Port 5034 service health. |
| **00:30 - 01:00** | Phase 2 | Corridor Selection & YOLO Bounding Box Canvas | Interactive selection of Urban Arterial Road 12 (Downtown Junction) and real-time canvas rendering of asphalt lane markings with D40 pothole bounding boxes. |
| **01:00 - 01:30** | Phase 3 | Pavement Condition Index (PCI) & Roughness (IRI) | Detailed readout of ASTM D6433 PCI rating (FAIR, 62.4) and ASTM E1926 International Roughness Index (3.42 m/km) with repair cost estimates. |
| **01:30 - 02:00** | Phase 4 | Critical Wear Simulation & Emergency Resurfacing | Simulation of high-density defect cluster on Industrial Ring Road, dropping PCI to critical 10.5 and triggering emergency POOR resurfacing alert. |
| **02:00 - 02:30** | Phase 5 | Municipal Work Orders (MWO) Dispatch | Review of active contractor work orders (MWO-2026-401) for cold asphalt milling and dispatch of new municipal remediation orders. |
| **02:30 - 03:00** | Phase 6 | DOT Regulatory Compliance & Relational SQLite WAL Ledger | Immutable audit trail of all road surveys and contractor work orders stored with ISO-8601 UTC timestamps in SQLite WAL mode. |
