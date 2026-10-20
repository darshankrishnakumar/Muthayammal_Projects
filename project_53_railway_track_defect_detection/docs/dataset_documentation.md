# Dataset Documentation: PROJECT-053 Multi-Corridor Telemetry Corpus

## 1. Overview
- **File**: `source_code/data/railway_telemetry_6000.csv`
- **Total Records**: Exactly 6,000 physical track inspection rows + 1 header row.
- **Null Fields**: 0 missing values across all 27 columns.

## 2. Corridor Archetypes (1,500 records each)
1. **High-Speed Line 1 Westbound**: Modern passenger corridor (250 km/h design speed).
2. **Heavy Freight Line 2 Northbound**: Heavy-haul corridor (30-ton axle loads, high RCF).
3. **Metro Suburban Line 3 Southbound**: Commuter line with frequent stops, high joint batter.
4. **Mountain Pass Switch & Turnout Corridor**: High-curvature turnouts with severe cant deficiency.

## 3. Class Balance
- Clean Rail Head: 52% (Nominal operations)
- Minor/Moderate Defects: 33% (Scheduled maintenance)
- Critical Priority Defects: 15% (Urgent remediation / speed restriction)
