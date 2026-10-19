# Project 31: Dataset & Hydrological Preprocessing

## 1. Dataset Telemetry Structure
The dataset comprises 5,800 records distributed across 5 diverse urban catchments:
- **Bay Coastal Lowlands**: 3.2m DEM, Tidal Estuary, Low drainage, high surge vulnerability.
- **Riverside Embankment District**: 6.5m DEM, Alluvial river plain, 6.0m crest limit.
- **Downtown Metropolitan Core**: 14.0m DEM, Urban concrete canyon, high population density.
- **Industrial Valley Sector**: 11.0m DEM, Alluvial valley basin, hazardous manufacturing.
- **Upland Ridge Buffer**: 85.0m DEM, Highland plateau, safe evacuation sanctuary.

## 2. Feature Definitions
| Feature Name | Type | Range | Description |
|---|---|---|---|
| `rainfall_mm` | Float | 2.0 - 290.0 mm | Cumulative precipitation |
| `river_stage_m` | Float | 1.2 - 16.0 m | River gauge water height |
| `river_threshold_m` | Float | 4.5 - 14.0 m | Bankfull danger crest limit |
| `soil_moisture` | Float | 0.20 - 1.00 | Volumetric saturation ratio |
| `storm_surge_m` | Float | 0.0 - 3.2 m | Tidal marine elevation push |
| `dem_elevation_m` | Float | 3.2 - 85.0 m | Topographic elevation above sea level |
| `drainage_score` | Float | 1.0 - 4.0 | Municipal drainage rating |
| `crest_exceedance_ratio` | Float | 0.2 - 1.8 | river_stage / threshold |

Normalized using z-score normalization parameters stored in `hydro_scalers.json`.
