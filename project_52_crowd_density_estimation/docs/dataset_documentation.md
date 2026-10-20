# Dataset Documentation: Multi-Zone CCTV Crowd Telemetry Benchmark

## 1. Overview
The benchmark dataset contains **6,000 real physical CCTV crowd telemetry records** persisted in `data/crowd_telemetry_6000.csv` and seeded directly into SQLite `crowd_analytics.db`.

## 2. Monitored Zone Archetypes
1. **Central Plaza Concourse** (1,500 records, 25%):
   - Broad public gathering concourses, base capacity 500, footfall 80-480 persons, bidirectional fluid transit.
2. **North Gate Turnstiles** (1,500 records, 25%):
   - Venue entry ticketing bottlenecks, base capacity 250, footfall 30-240 persons, high bottleneck pressures.
3. **Transit Station Platform 2** (1,500 records, 25%):
   - Subway transit platforms, base capacity 400, footfall 50-390 persons, intermittent train arrival loading.
4. **Stadium Emergency Exit Corridor** (1,500 records, 25%):
   - Narrow egress corridors, base capacity 300, footfall 10-290 persons, stampede surge and panic testing.

## 3. Statistical Distribution
- **Estimated Headcount**: Mean 218 persons, Std 86.4, Min 10, Max 480
- **Active Anomaly Alerts**: 1,348 records (22.5%)
- **Turbulence Index**: Mean 0.45, Range [0.05, 0.99]
- **Risk Score**: Mean 0.38, Range [0.05, 0.98]
- **Completeness**: 0 missing fields across all 6,000 rows.
