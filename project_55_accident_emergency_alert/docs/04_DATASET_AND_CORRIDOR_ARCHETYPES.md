# 04 — Dataset & Corridor Archetypes

## Benchmark Dataset Overview
- **File Location**: `data/accident_telemetry_6000.csv`
- **Total Records**: 6,000 verified physical records
- **Null / Missing Values**: 0 (100% schema integrity)
- **Columns**: 27 telemetry, environmental, and CAD columns

## Corridor Archetypes
```
+------------------------+------------------------------------+--------------+-------------------------+
| Camera Identifier      | Corridor Name & Roadway Type       | Speed Limit  | Primary Collision Risk  |
+------------------------+------------------------------------+--------------+-------------------------+
| CAM-HWY-101-NORTH      | Interstate 101 Expressway (Freeway)| 110 km/h     | High-Speed Rollover     |
| CAM-URBAN-MAIN-5TH     | Downtown Main St & 5th Ave (Urban) | 50 km/h      | Perpendicular T-Bone    |
| CAM-RURAL-PASS-RT9     | Route 9 Mountain Pass (Rural Turn) | 65 km/h      | Guardrail Spinout Strike|
| CAM-PORT-LOGISTICS-WAY | Industrial Port Logistics Loop     | 45 km/h      | Heavy Truck Rear-End    |
+------------------------+------------------------------------+--------------+-------------------------+
```

## Telemetry Feature Columns
1. `record_id`: Unique deterministic incident identifier (`INC-2026-XXXXX-XXXX`)
2. `timestamp`: ISO-8601 UTC timestamp
3. `camera_id`: Foreign key reference to monitored roadside camera
4. `deceleration_g`: Peak longitudinal deceleration in g-force
5. `orientation_yaw_deg`: Relative vehicle rotation angle (-180° to +180°)
6. `trajectory_deviation_m`: Lateral excursion from lane center in meters
7. `impact_force_kn`: Estimated structural collision force in kilonewtons
8. `delta_v_kph`: Velocity change magnitude in km/h
9. `post_impact_immobility_sec`: Duration of vehicle standstill following impact
10. `actual_speed_kph`: Pre-crash travelling speed
11. `speed_limit_kph`: Corridor posted legal speed limit
12. `vehicles_involved`: Total vehicle count involved in collision
13. `road_friction_coeff`: Roadway surface friction coefficient (0.35 to 0.85)
14. `visibility_m`: Optical atmospheric visibility in meters (100m to 2000m)
15. `ambient_lux`: Ambient lighting illuminance (20 lux to 1000 lux)
16. `rollover_detected`: Boolean flag indicating vehicle roof/quarter inversion
17. `severity`: Categorical classification (`Critical`, `Severe`, `Moderate`, `Minor`)
18. `priority`: Triage urgency code (`P1-Critical`, `P2-High`, `P3-Medium`, `P4-Low`)
19. `evidence_hash`: Deterministic SHA-256 tamper-evident record hash
