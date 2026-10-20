# Dataset Documentation — PROJECT-048
## Multi-Spectral Food Quality Telemetry Benchmark (6,000 Records)

### 1. Overview
The benchmark dataset is located at `source_code/data/food_telemetry_6000.csv` and contains exactly 6,000 physical telemetry records spanning 4 perishable sectors:
- **MEAT_POULTRY**: Prime Ribeye Beef, Free-Range Chicken Breast, Heritage Pork Tenderloin, Atlantic Salmon Fillet.
- **FRESH_PRODUCE**: Organic Baby Spinach, Hass Avocado Pack, Strawberries Clamshell, Crisp Romaine Lettuce.
- **DAIRY**: Artisan Farm Cheddar, Grade-A Whole Milk, Greek Whole Yogurt, Cultured Salted Butter.
- **BAKERY**: Artisan Sourdough Loaves, Butter Croissant 4-Pack, Brioche Buns, Multi-Grain Hearth Loaf.

### 2. Feature Definitions & Kinematics
1. `storage_temp_c`: Ambient storage temperature in Celsius (-1.5°C to 14.5°C).
2. `relative_humidity_pct`: Relative humidity percentage (35% to 98%).
3. `storage_duration_hours`: Elapsed time in storage (2 to 192 hours).
4. `browning_index`: Spectrophotometric oxidation index (0.5 to 30.0).
5. `tvbn_mg_per_100g`: Total Volatile Basic Nitrogen accumulation (2.0 to 48.0 mg/100g).
6. `ph_level`: Acidity/alkalinity measure (4.4 to 7.5).
7. `ethylene_concentration_ppm`: Produce respiration gas emission (0.01 to 24.0 ppm).
8. `moisture_content_pct`: Moisture percentage (30% to 92%).
9. `bacterial_log_cfu_g`: Aerobic plate bacterial count (1.5 to 8.8 log CFU/g).
10. `reflectance_ratio_650_850`: Optical ratio of 650 nm to 850 nm reflectance.
11. `freshness_score`: Continuous composite freshness index (5.0 to 99.5).
12. `deterioration_stage`: Quality classification (STAGE_1_FRESH, STAGE_2_MARGINAL, STAGE_3_DETERIORATED).
13. `remaining_shelf_life_days`: Dynamic kinetic shelf life (0.0 to 20.0 days).
14. `spoilage_risk_pct`: Spoilage probability (0.0% to 100.0%).
15. `microbial_risk_pct`: Pathogen proliferation risk (0.0% to 100.0%).
16. `cold_chain_compliance_score`: HACCP temperature compliance (15.0% to 100.0%).

### 3. Data Integrity & Validation
- Null values: 0 across all 21 columns.
- Arrhenius temperature kinetic effect validated: cold storage extends shelf life.
- Bacterial count strongly correlates (>0.70) with spoilage risk.
