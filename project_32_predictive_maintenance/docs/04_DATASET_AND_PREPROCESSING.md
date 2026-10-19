# Project 32: Dataset & Sensor Preprocessing

## 1. Machine Fleet Composition
The dataset comprises 6,000 records distributed across 5 industrial rotating machines:
- **Screw Compressor A-101**: 2,980 RPM, Rotary Screw Compressor, High criticality.
- **Centrifugal Pump B-204**: 1,480 RPM, Slurry Circulation Pump, Critical.
- **Induction Motor C-302**: 1,780 RPM, 3-Phase 350kW Motor, Medium criticality.
- **Gas Turbine Generator D-401**: 5,400 RPM, Co-Gen Gas Turbine, Critical.
- **Conveyor Drive Unit E-505**: 720 RPM, Heavy Ore Conveyor Drive, Low criticality.

## 2. Feature Definitions
| Feature Name | Type | Unit | Description |
|---|---|---|---|
| `temperature_c` | Float | °C | Bearing race temperature |
| `vibration_mm_s` | Float | mm/s | Casing vibration velocity RMS |
| `pressure_bar` | Float | bar | Fluid discharge pressure |
| `rpm` | Float | RPM | Shaft angular velocity |
| `oil_viscosity_cst` | Float | cSt | Lubrication oil dynamic viscosity |
| `acoustic_emission_db` | Float | dB | High-frequency ultrasonic emission |
| `fft_harmonic_ratio` | Float | ratio | 2X to 1X harmonic ratio |
| `bearing_defect_freq_energy` | Float | energy | BPFO/BPFI defect frequency energy |

Normalized using z-score normalization parameters stored in `pdm_scalers.json`.
