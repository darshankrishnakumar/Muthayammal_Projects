# Demonstration & Walkthrough Script: Smart Energy Consumption Forecasting & Dynamic Peak Shaving (PROJECT-051)

## Overview
- **Project Identifier**: PROJECT-051
- **Module**: `project_51_energy_consumption_forecasting`
- **Assigned Port**: `5051`
- **Video Target Duration**: `180.000000 seconds (03:00.000)`
- **Format**: `1280x800 H.264 MP4 (720 frames @ 4.0 fps)`
- **Primary Architecture**: Dual PyTorch Networks (`MultiHorizonEnergyLSTM` [145,496 params] + `GridPeakAndCarbonEmissionRegressorNet` [12,613 params] = 158,109 params total)

## 6-Phase Script Sequence (30 Seconds per Phase)
1. **00:00 - 00:30 | Phase 1: Title & System Overview**
   - Live dashboard display on Port 5051 with Dual PyTorch Engines indicator and SQLite WAL badge.
   - Walk through fleet KPI cards: 6,000 Active Dispatch Plans, 22.0% Mean Peak Shaving, $745,200.00 Daily Fleet Cost Savings.
2. **00:30 - 01:00 | Phase 2: 24-Hour Load Demand Chart HUD**
   - Examine Chart.js load curves: Uncontrolled Baseline (peaks at 684.2 kW) vs. Optimized Shaving (capped at 530.9 kW).
   - Review marginal carbon intensity tracking (312.4 gCO2/kWh) and off-peak load shifting mechanism.
3. **01:00 - 01:30 | Phase 3: Facility Optimization: Commercial Campus & Industrial Plant**
   - Demonstrate Tech Campus Science Complex A (Commercial Office): 22.4% shaving, $118.50/day savings, 142.0 kg CO2 avoided.
   - Dispatch Automotive Stamping Assembly 4 (Industrial Plant): heavy 3-phase machinery shifted to night off-peak window, saving $285.40/day.
4. **01:30 - 02:00 | Phase 4: Facility Optimization: Hyperscale Cloud DC & Hospital Complex**
   - Dispatch Hyperscale Cloud Facility DC-2 (Data Center): thermal chilled water buffer dispatch saving $310.20/day.
   - Dispatch Metro General Hospital Complex: non-deferrable ICU critical power maintained with 100% emergency reserve margin.
5. **02:00 - 02:30 | Phase 5: Active Optimization Plans Registry & SQLite WAL Persistence**
   - Scroll through the 6,000-record optimization plans registry in `energy_plans`.
   - Inspect relational schema, zero-null integrity, and instant ACID query performance.
6. **02:30 - 03:00 | Phase 6: Cryptographic Audit Ledger & Continuous Hash Chaining**
   - Verify Genesis Block #0 with 64-character deterministic zero-hash predecessor.
   - Demonstrate continuous SHA-256 block hash chaining and tamper-evident audit logging for ISO 50001 compliance.
