# Dataset Documentation: Commercial & Industrial Energy Telemetry Benchmark

## 1. Overview
The benchmark dataset contains **6,000 real physical facility telemetry records** persisted in `data/energy_telemetry_6000.csv` and seeded directly into SQLite `energy.db`.

## 2. Facility Archetypes
1. **Commercial Office Campus** (1,500 records, 25%):
   - Daytime occupancy peaking 09:00-17:00, significant HVAC cooling loads, base loads 350-550 kW.
2. **Industrial Manufacturing Plant** (1,500 records, 25%):
   - Heavy 3-phase machinery, base loads 700-1,100 kW, extensive night-shift load shifting flexibility.
3. **Hyperscale Data Center** (1,500 records, 25%):
   - Continuous 24/7 compute base load 1,000-1,500 kW, chilled water thermal storage buffering.
4. **Municipal Hospital Complex** (1,500 records, 25%):
   - Critical life-safety circuits, non-deferrable ICU/surgical suites, base loads 500-750 kW.

## 3. Statistical Distribution
- **Energy Consumption**: Mean 485.6 kWh, Std 142.3 kWh, Min 120.0 kWh, Max 1,450.0 kWh
- **Peak Shaving**: Mean 22.0%, Std 4.5%, Range [10.0%, 35.0%]
- **Daily Cost Savings**: Mean $124.20 per facility, Fleet Total: $745,200.00
- **Avoided CO2**: Mean 148.5 kg/day per facility
- **Completeness**: 0 missing fields across all 6,000 rows.
