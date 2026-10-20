# Industrial Telemetry Dataset Documentation (PROJECT-046)

## Overview
- **File**: `data/manufacturing_telemetry_6000.csv`
- **Record Count**: 6,000 physical component inspection records.
- **Attributes**: 12 tabular columns capturing optical, dimensional, and mechanical parameters.

## Field Schema
1. `part_id`: Unique industrial serial string (`PART-2026-10000` to `PART-2026-15999`).
2. `assembly_line`: One of 4 manufacturing production lines.
3. `part_type`: `PCB_BOARD`, `MACHINED_GEAR`, `METALLIC_CASING`, `TURBINE_BLADE`.
4. `inspection_verdict`: `PASS` (68.2%) or `REJECT` (31.8%).
5. `defect_type`: `NONE`, `SCRATCH`, `CRACK`, `DENT`, `MISSING_COMPONENT`.
6. `severity_score`: Continuous damage score [0.0, 100.0]%.
7. `defect_area_pct`: Continuous surface defect coverage [0.0, 100.0]%.
8. `surface_roughness_ra`: ISO 4287 roughness parameter [0.1, 10.0] um.
9. `pneumatic_ejection_confidence`: Solenoid firing probability [0.0, 100.0]%.
10. `inspection_cycle_time_ms`: End-to-end edge processing time [9.5, 16.5] ms.
11. `model_confidence`: Softmax probability score [0.940, 0.999].
12. `actuator_action`: `ROUTE_CONVEYOR` or `TRIGGER_PNEUMATIC_EJECT`.
