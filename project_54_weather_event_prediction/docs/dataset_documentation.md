# Dataset Documentation: PROJECT-054 Multi-Station Telemetry Corpus

## 1. Overview
- **File**: `source_code/data/weather_telemetry_6000.csv`
- **Total Records**: Exactly 6,000 meteorological observation rows + 1 header row.
- **Null Fields**: 0 missing values across all 27 columns.

## 2. Station Archetypes (1,500 records each)
1. **Coastal Maritime Radar Station 01**: Low elevation (12m), high marine humidity, coastal gales.
2. **Plains Supercell Radar Station 02**: Continental interior (340m), severe supercells, high CAPE (>3,000 J/kg).
3. **Mountain Alpine Pass Radar Station 03**: High altitude (1,850m), orographic lift, extreme gap winds.
4. **Urban Convective Basin Radar Station 04**: Low basin (125m), thermal dome island, flash flood downpours.

## 3. Event Class Balance
- Normal Transition: 50% (Routine synoptic conditions)
- Heavy Rainfall: 20% (PWAT > 45mm, rain rate > 35mm/h)
- Severe Thunderstorm: 15% (Reflectivity > 50 dBZ, high CAPE, lightning)
- Gale Wind Storm: 10% (Sustained gusts > 75 km/h)
- Heatwave Spike: 5% (Thermal dome anomaly)
