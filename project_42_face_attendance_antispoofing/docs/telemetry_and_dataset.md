# Telemetry Benchmark Dataset (6,000 Records)

## Dataset Specifications
- **File Location**: `source_code/data/face_attendance_telemetry_6000.csv`
- **Total Records**: Exactly 6,000 rows (plus header row).
- **Class Balance**:
  - 3,000 Genuine Live Human authentications (50.0%).
  - 3,000 Presentation Attack attempts (50.0%).
- **Adversarial Breakdown**:
  - 1,000 2D Printed Paper Photo Attacks (`PRINT_ATTACK_2D`).
  - 1,000 4K OLED Video Replay Attacks (`SCREEN_REPLAY_ATTACK`).
  - 1,000 3D Silicone Hyper-Realistic Mask Attacks (`SILICONE_3D_MASK`).
- **Student Subject Allocation**:
  - Balanced identically across 5 enrolled subjects (1,200 records each).
- **Scalers & Metadata**:
  - `face_scalers.json`: Contains precomputed feature means and standard deviations for Z-score normalization.
  - `model_metadata.json`: Contains model architectural parameters and validation benchmarks.
