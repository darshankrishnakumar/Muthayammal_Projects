# Solid Waste Sorting Telemetry Dataset Guide (ASTM D5231)

## 1. Overview
The benchmark dataset (`waste_classification_telemetry_6000.csv`) comprises 6,000 multi-modal physical survey records captured across 6 discrete municipal recyclable streams (1,000 records per class):
1. **Plastic**: PET beverage bottles, HDPE jugs, polypropylene containers.
2. **Glass**: Flint jars, amber beverage bottles, cullet fragments.
3. **Metal**: Aluminum beverage cans, tin-plated steel food canisters.
4. **Paper**: Deinked newsprint, office documents, envelopes.
5. **Cardboard**: Old Corrugated Cardboard (OCC), shipping boxes, cartonboard.
6. **Organic**: Post-consumer food scraps, produce trimmings, yard waste.

## 2. Feature Schema & Standards
| Feature Name | Unit | Type | Physical Range |
|---|---|---|---|
| `density_g_cm3` | g/cm³ | Float | 0.35 - 7.85 |
| `spectral_reflectance_nir` | Albedo [0-1] | Float | 0.15 - 0.99 |
| `opacity_pct` | % | Float | 2.0% - 100.0% |
| `surface_roughness_um` | um (Ra) | Float | 0.5 - 75.0 um |
| `moisture_content_pct` | % | Float | 0.1% - 85.0% |
| `rigidity_modulus_gpa` | GPa | Float | 0.05 - 120.0 GPa |
| `magnetic_susceptibility` | Scalar [0-1] | Float | 0.0 - 0.98 |
| `carbon_footprint_kg_co2` | kg CO2e / kg | Float | 0.1 - 14.0 |
| `category` | String | Categorical | Plastic, Glass, Metal, Paper, Cardboard, Organic |
| `recyclability_score` | % | Float | 0.0% - 100.0% |
| `contamination_risk` | Probability [0-1] | Float | 0.0 - 1.0 |
