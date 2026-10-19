# Walkthrough Timestamps: URBAN FLOOD RISK PREDICTION & EARLY WARNING SYSTEM (PROJECT-031)

Exact Target Video Duration: **180.000 Seconds (03:00.00)**  
Video Specifications: **1280x800 H.264 MP4 @ 24fps Constant Framerate**

| Timestamp Range | Phase | Phase Description & Operational Demonstration |
|---|---|---|
| **00:00 - 00:30** | Phase 1 | **System Overview & Hydrological Metric Strip**: Real-time situation indicators (Total Assessments, Critical Zones, Warning Zones, Population at Risk), `/api/health` verification on Port 5031, monitored catchment carousel across 5 river basins. |
| **00:30 - 01:00** | Phase 2 | **Catchment Topography & River Stage Gauges**: Dynamic selection of Bay Coastal Lowlands (3.2m DEM) and Downtown Core (14.0m DEM), river level gauge vs crest threshold comparator, and baseline soil moisture telemetry. |
| **01:00 - 01:30** | Phase 3 | **Severe Cloudburst Deluge & Critical Red Alert**: PyTorch forward inference on Bay Coastal Lowlands under 220mm rainfall and 2.2m storm surge, immediate CRITICAL RED ALERT trigger (86.0% risk), and mandatory ground floor evacuation protocol. |
| **01:30 - 02:00** | Phase 4 | **Inundation Depth Simulation & Contour Mapping**: Real-time animated canvas rendering standing floodwater depth (1.45m - 2.78m), physical terrain flow routing, and backwater ponding visualization. |
| **02:00 - 02:30** | Phase 5 | **Evacuation Lead-Time Forecasting & Emergency Dispatch**: InundationDepthRegressorNet lead time output (2.5 hours warning), emergency barrier activation, and automated `/api/dispatch` municipal logging. |
| **02:30 - 03:00** | Phase 6 | **Broadcast History Ledger & SQLite WAL Persistence**: Historical flood warning broadcast log inspection, ACID transactional durability, SQLite Write-Ahead Logging integrity, and 31/31 QA automated test suite conformance. |
