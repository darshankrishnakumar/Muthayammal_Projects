# 04. Atmospheric Data Pipeline & Corpus Engineering (PROJECT-028)

## Monitoring Station Network
The atmospheric database comprises 5,500 hourly records across 10 international monitoring stations:

| Station ID | City | Country | Baseline AQI | Ambient Temp | Relative Humidity | Wind Speed | Mixing Height |
|---|---|---|---|---|---|---|---|
| `ST-DEL-01` | Delhi | India | 235 (Hazardous Peaks) | 31.5°C | 64.0% | 6.2 km/h | 620 m |
| `ST-BOM-02` | Mumbai | India | 128 (Coastal Metro) | 29.0°C | 78.0% | 14.5 km/h | 850 m |
| `ST-BLR-03` | Bengaluru | India | 68 (Plateau) | 24.2°C | 62.0% | 11.0 km/h | 920 m |
| `ST-MAA-04` | Chennai | India | 82 (Maritime Bay) | 32.0°C | 81.0% | 15.2 km/h | 890 m |
| `ST-CCU-05` | Kolkata | India | 164 (Alluvial Basin) | 30.5°C | 75.0% | 8.4 km/h | 710 m |
| `ST-HYD-06` | Hyderabad | India | 105 (Deccan Semi-Arid)| 28.0°C | 60.0% | 9.8 km/h | 830 m |
| `ST-LON-07` | London | UK | 42 (ULEZ Baseline) | 16.0°C | 68.0% | 18.2 km/h | 1100 m |
| `ST-NYC-08` | New York | USA | 48 (Atlantic Coastal) | 21.0°C | 55.0% | 12.0 km/h | 1050 m |
| `ST-TYO-09` | Tokyo | Japan | 35 (Oceanic Ventilation) | 22.0°C | 58.0% | 10.4 km/h | 1150 m |
| `ST-PAR-10` | Paris | France | 52 (Continental) | 18.5°C | 64.0% | 13.5 km/h | 1020 m |

## Dataset Files
- `source_code/data/air_quality_timeseries.csv`: 5,500 rows with 20 columns.
- `source_code/data/air_quality_timeseries.json`: Structured array of records.
- `source_code/backend/aqi_scalers.json`: Empirical means and standard deviations.
