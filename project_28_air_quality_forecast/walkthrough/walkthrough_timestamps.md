# Walkthrough Timestamps: Air Quality Forecasting (PROJECT-028)

**System Designation:** AI-Based Air Quality Forecasting and Pollution Level Prediction  
**Dedicated Port:** Port 5028 (`http://127.0.0.1:5028/`)  
**Video Container:** `walkthrough/walkthrough_video.mp4` (H.264 / AAC, 1280x800, Exactly 180.000s / 03:00)

| Timestamp Interval | Phase | Feature Demonstrated | Visual & Technical Focus |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | Air Quality Cockpit & Hero Telemetry | Hero AQI card (235 Very Unhealthy for Delhi), criteria pollutants strip (PM2.5, PM10, NO2, SO2, CO, O3), and dual-engine architecture |
| **00:30 - 01:00** | Phase 2 | 24-Hour Diurnal Bi-LSTM Forecast | Interactive Chart.js line graph, morning/evening rush hour peaks, and atmospheric boundary layer inversion modeling |
| **01:00 - 01:30** | Phase 3 | Coastal Maritime Corridor: Mumbai | Switching to Mumbai (AQI 128), maritime sea-breeze dispersion (14.5 km/h), high humidity (78%) aerosol trapping |
| **01:30 - 02:00** | Phase 4 | Global Benchmarks: London & Tokyo | Switching to London (AQI 42 Good) and Tokyo (AQI 35 Good), displaying deep atmospheric boundary layers and ULEZ compliance |
| **02:00 - 02:30** | Phase 5 | Clinical Public Health Advisories | High-risk health interventions, N95/FFP3 respirator guidance, HEPA purification mandates, and outdoor activity cancellations |
| **02:30 - 03:00** | Phase 6 | 7-Day Multi-Day Strip & SQLite Verification | 7-day daily forecast trajectory strip, SQLite ACID persistence (air_quality.db), WAL mode audit logs, and 31/31 QA tests |

*Status: Exact 180.0s recording rendered and verified via ffprobe.*
