# Clinical Dataset & Machine Learning Pipeline Details

## 1. Dataset Provenance & Features

The model was trained on authentic pediatric walking trials derived from the SimTK Pediatric Gait Repository, augmented with clinically validated pediatric records.

- **Primary Dataset**: `source_code/ml-service/data/real_child_gait_features.csv`
- **Volume**: 21 clinical motion capture trials across 14 unique pediatric participants.
- **Diagnostic Distribution**:
  - `Normal` (Typically Developing): 5 children (TD1–TD5)
  - `Diplegic` (Bilateral Crouch Gait / Spastic Cerebral Palsy): 4 children (DICP1–DICP4)
  - `Hemiplegic` (Unilateral Spastic Asymmetry): 5 children (HECP1–HECP5)

### Feature Dictionary

| Feature Name | Clinical Description | Typical Normal Range | Typical Pathological Range |
| :--- | :--- | :--- | :--- |
| `walking_speed` | Forward linear walking velocity (m/s) | 1.10 – 1.35 m/s | 0.50 – 0.95 m/s |
| `stride_length` | Consecutive contact distance for same foot (cm) | 75.0 – 95.0 cm | 45.0 – 65.0 cm |
| `step_duration` | Time duration for single step support + swing (s) | 0.45 – 0.55 s | 0.65 – 0.90 s |
| `cadence` | Locomotion rhythm (steps per minute) | 110 – 130 steps/min | 65 – 95 steps/min |
| `pelvic_tilt` | Forward sagittal tilt angle of pelvis (degrees) | 2.0 – 6.0° | 10.0 – 18.0° |
| `step_asymmetry` | Ratio of temporal disparity between left & right steps | < 0.05 | > 0.15 (Hemiplegia) |
| `peak_vertical_force_bw` | Maximum ground reaction force (% body weight) | 110 – 125% BW | < 95% BW or > 140% BW |

---

## 2. Zero-Leakage Participant Partitioning

To avoid identity leakage, trials from the same child never cross partitions:

- **Training Set (52.4%)**: 11 trials from 8 children (`['TD1', 'TD2', 'TD3', 'HECP1', 'HECP2', 'HECP3', 'DICP1', 'DICP2']`)
- **Validation Set (33.3%)**: 7 trials from 3 children (`['TD4', 'HECP4', 'DICP3']`)
- **Held-Out Test Set (14.3%)**: 3 trials from 3 children (`['TD5', 'HECP5', 'DICP4']`)

All preprocessing scalers are fit strictly on the Training Set.

---

## 3. Multi-Model Benchmarking

| Algorithm | Test Accuracy | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | One-vs-Rest ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Tuned)** | **66.67%** | **0.5000** | **0.6667** | **0.5556** | **1.0000** |
| Random Forest (Baseline) | 66.67% | 0.5000 | 0.6667 | 0.5556 | 0.5000 |
| Gradient Boosting (GBDT) | 33.33% | 0.1111 | 0.3333 | 0.1667 | 0.5000 |
| Support Vector Machine (SVM) | 33.33% | 0.1111 | 0.3333 | 0.1667 | 0.5000 |
| Decision Tree (CART) | 0.00% | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| K-Nearest Neighbors (KNN) | 0.00% | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### Optimal Hyperparameters
- `n_estimators`: 50
- `max_depth`: 3
- `min_samples_split`: 2
- `max_features`: `sqrt`
- `random_state`: 42
