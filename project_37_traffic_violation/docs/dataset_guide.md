# Dataset Guide: Multi-Modal Traffic Telemetry (6,000 Records)

## 1. Overview
The empirical telemetry dataset is persisted at `source_code/data/traffic_violation_telemetry_6000.csv`. It contains 6,000 physical and optical records balanced across eight statutory traffic violation categories.

## 2. Feature Schema

| Field Name | Type | Range / Domain | Description |
|---|---|---|---|
| `record_id` | Integer | 1 - 6000 | Primary sequence identifier |
| `vehicle_id` | String | VEH-00001 - VEH-06000 | Unique vehicle entity tag |
| `license_plate` | String | TN[10-99]A[1000-9999] | ANPR optical plate string |
| `intersection_id` | String | INT-01, INT-02, INT-03, INT-04 | Monitored junction node |
| `vehicle_type` | String | Car, Motorcycle, Truck, Bus, Auto, Van | Categorical vehicle class |
| `speed_kmh` | Float | 20.0 - 140.0 km/h | Radar observed velocity |
| `speed_limit` | Float | 50.0, 60.0, 80.0 km/h | Statutory speed threshold |
| `speed_delta` | Float | speed_kmh - speed_limit | Net overspeed margin |
| `traffic_light_state` | Integer | 0: Red, 1: Amber, 2: Green | Traffic signal phase |
| `distance_to_stop_line_m` | Float | -8.0m to 45.0m | Stop line displacement |
| `lane_position_offset_m` | Float | -1.8m to 1.8m | Lateral lane center offset |
| `helmet_detected` | Integer | 0 or 1 | Two-wheeler rider headgear |
| `seatbelt_detected` | Integer | 0 or 1 | Four-wheeler restraint |
| `mobile_phone_detected` | Integer | 0 or 1 | Distracted handheld device |
| `heading_degrees` | Float | 0.0° - 180.0° | Traffic flow alignment |
| `traffic_density` | Float | 15.0 - 85.0 veh/km | Correlated congestion level |
| `optical_visibility` | Float | 0.30 - 1.00 | Weather/glare attenuation |
| `violation_class_idx` | Integer | 0 to 7 | Supervised classification target |
| `severity_index` | Float | 0.0 - 100.0 | Ground-truth hazard severity |
| `collision_risk` | Float | 0.0000 - 1.0000 | Ground-truth collision probability |
| `fine_inr` | Integer | 0, 500, 1000, 1500, 2000, 5000 | Statutory MVA statutory fine |
