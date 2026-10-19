# Dataset Guide: RDD2022 Road Damage Survey Benchmark (PROJECT-034)

## 1. Provenance
The dataset is established upon the international Road Damage Dataset 2022 (RDD2022) multi-country benchmark.

## 2. Dataset Structure
- File: `source_code/data/rdd2022_pavement_surveys_6000.csv`
- Total Records: 6,000 multi-variate road inspection records across 5 commercial corridors.
- Train / Test Partition: 4,800 train records (80%), 1,200 holdout test records (20%).

## 3. Telemetry Feature Columns
1. `survey_id`: Unique identifier (`SRV-00001` to `SRV-06000`).
2. `sector_id`: Roadway sector code (`SEC-NORTH-01` to `SEC-MTN-05`).
3. `sector_name`: Canonical roadway corridor title.
4. `damage_class_idx`: Integer class index (0 to 4).
5. `damage_code`: Standard distress code (D40, D20, D00, D10, D43).
6. `damage_name`: Canonical distress classification.
7. `damage_severity`: Qualitative tier (HIGH, MEDIUM).
8. `damaged_area_sqm`: Damaged pavement surface area in square meters.
9. `pothole_depth_cm`: Maximum vertical depression depth in centimeters.
10. `crack_width_mm`: Maximum crack aperture in millimeters.
11. `traffic_volume_vpd`: Average daily traffic volume in thousands (k-VPD).
12. `heavy_axle_pct`: Percentage of heavy commercial freight vehicles.
13. `pavement_age_years`: Years elapsed since last major asphalt resurfacing.
14. `drainage_quality_idx`: Pavement drainage efficiency index (0.2 to 1.0).
15. `freeze_thaw_cycles`: Annual seasonal freeze-thaw count.
16. `pci_score`: Pavement Condition Index score (0 to 100).
17. `pci_rating`: ASTM D6433 condition category (GOOD, FAIR, POOR).
18. `iri_roughness_m_km`: International Roughness Index in m/km.
19. `repair_cost_usd`: Estimated remediation contractor cost.
20. `recommended_action`: Standardized civil asphalt repair technique.
