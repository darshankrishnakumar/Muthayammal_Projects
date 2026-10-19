# Dataset Guide: NASA C-MAPSS Turbofan Degradation (PROJECT-033)

## 1. Provenance
The dataset is modeled after the NASA Ames Prognostics Center of Excellence Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) benchmark (subsets FD001 through FD004).

## 2. Dataset Structure
- File: `source_code/data/nasa_cmapss_turbofan_6000.csv`
- Total Records: 6,000 multi-variate telemetry records across 5 aircraft components.
- Train / Test Partition: 4,800 train records (80%), 1,200 holdout test records (20%).

## 3. Telemetry Feature Columns
1. `record_id`: Unique identifier (`REC-00001` through `REC-06000`).
2. `component_id`: Subsystem code (`COMP-TURB-01` to `COMP-LPT-05`).
3. `component_name`: Canonical name of the powerplant component.
4. `engine_model`: Commercial turbofan model (`CFM56-7B`, `GE90-115B`, `Trent 1000`, `PW1100G`, `CF34-8E`).
5. `max_design_cycles`: Manufacturer certified operational lifecycle.
6. `flight_cycles_completed`: Cumulative flight cycles since last overhaul.
7. `cycle_ratio`: Completed cycles / max design cycles (0.05 to 1.05).
8. `t50_lpt_outlet_temp_r`: LPT exit exhaust gas temperature (°R).
9. `p30_hpc_pressure_psia`: High-pressure compressor static discharge pressure (psia).
10. `nc_core_speed_rpm`: High-pressure core spool speed (RPM).
11. `nf_fan_speed_rpm`: Low-pressure fan spool speed (RPM).
12. `fuel_flow_ratio_pps_psi`: Ratio of fuel flow to compressor static pressure.
13. `egt_margin_deg_c`: Exhaust Gas Temperature Margin (°C).
14. `vibration_broadband_g`: Accelerometer broadband vibration (g RMS).
15. `health_score`: Continuous health metric (0.0% to 100.0%).
16. `rul_cycles`: Target remaining useful life flight cycles.
17. `status_idx`: Regulatory classification index (0, 1, 2).
18. `airworthiness_status`: FAA status string.
