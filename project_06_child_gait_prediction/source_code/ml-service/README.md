# Child Gait Prediction ML Pipeline

A machine learning pipeline for analyzing real pediatric gait motion-capture data from the **SimTK CP Child Gait Dataset** and predicting child gait classifications:
- **`Normal`** (Typically Developing / TD)
- **`Hemiplegic`** (Unilateral Cerebral Palsy / CP_HE)
- **`Diplegic`** (Bilateral Cerebral Palsy / CP_DI)

---

## 1. Dataset Source & Structure

- **Origin**: SimTK Pediatric Gait Motion-Capture Dataset
- **Raw Files**: 21 `.c3d` trials across 3 cohorts in `ml-service/data/raw/`:
  - `td/`: 8 trials (Typically Developing)
  - `hecp/`: 7 trials (Hemiplegic Cerebral Palsy)
  - `dicp/`: 6 trials (Diplegic Cerebral Palsy)
- **Participant Metadata**: `ml-service/data/participant_information.xlsx`
  - 14 unique children (5 TD, 5 CP_HE, 4 CP_DI)
  - Demographics: Age (6.3–12.5 years), Gender (M/F), Body Weight, Height, GMFCS levels (1.0 & 2.0)
- **Instrumentation**:
  - Optical 3D point rate: **100.0 Hz** (Vicon Plug-in Gait marker protocol)
  - Analog force plate rate: **1,500.0 Hz** (Dual AMTI force plates recording 3D Ground Reaction Forces)
  - 16-channel surface electromyography (EMG)

---

## 2. Participant & Class Mapping

| Cohort Code | Clinical Meaning | Target Model Class | Participants | Total Trials |
|---|---|---|---|---|
| **TD** | Typically Developing | **Normal** | 5 (`TD1`, `TD2`, `TD3`, `TD4`, `TD5`) | 8 |
| **CP_HE** | Hemiplegic CP | **Hemiplegic** | 5 (`HECP1`, `HECP2`, `HECP3`, `HECP4`, `HECP5`) | 7 |
| **CP_DI** | Diplegic CP | **Diplegic** | 4 (`DICP1`, `DICP2`, `DICP3`, `DICP4`) | 6 |

---

## 3. Biomechanical Feature Engineering

Features were extracted directly from the 3D marker coordinates and force plate channels without synthetic data generation:

| Feature Name | Source | Calculation | Unit | Description |
|---|---|---|---|---|
| `walking_speed` | Sacrum/Pelvis trajectory | Forward linear displacement / duration | m/s | Mean linear velocity of pelvis center |
| `stride_length` | RHEE/LHEE 3D markers | Euclidean horizontal distance between ipsilateral strikes | cm | Distance covered in one full bilateral cycle |
| `step_duration` | RHEE/LHEE vertical minima | Time elapsed between contralateral heel strikes | s | Step duration per lower limb |
| `cadence` | Step duration | `60.0 / step_duration` | steps/min | Step frequency |
| `pelvic_tilt` | SACR & RASI/LASI plane | Sagittal angle relative to horizontal plane | degrees | Mean pelvic inclination |
| `step_asymmetry` | Left & Right step lengths | `\|Left - Right\| / (0.5 * (Left + Right))` | ratio | Bilateral step length discrepancy (diagnostic for Hemiplegic CP) |
| `peak_vertical_force_bw` | AMTI Force Plates (FZ1, FZ2) | `Peak |FZ| / (weight * 9.81) * 100` | %BW | Peak vertical ground reaction force normalized to body weight |

Full dictionary saved in [`ml-service/data/feature_dictionary.csv`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/data/feature_dictionary.csv).

---

## 4. Zero-Leakage Participant-Level Splitting

To guarantee zero data leakage, **all trials for any given participant are grouped exclusively into one split**:

- **Held-Out Test Set (3 children, 3 trials)**:
  - `TD5` (Normal), `HECP5` (Hemiplegic), `DICP4` (Diplegic)
  - Untouched during all training and hyperparameter search.
- **Validation Set (3 children, 7 trials)**:
  - `TD4` (3 trials), `HECP4` (1 trial), `DICP3` (3 trials)
- **Training Set (8 children, 11 trials)**:
  - `TD1` (2 trials), `TD2` (1 trial), `TD3` (1 trial)
  - `HECP1` (1 trial), `HECP2` (3 trials), `HECP3` (1 trial)
  - `DICP1` (1 trial), `DICP2` (1 trial)

---

## 5. Model Evaluation & Comparison Results

Evaluated on the held-out test participants (`TD5`, `HECP5`, `DICP4`):

| Model | Held-Out Test Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Validation F1 | Training Duration |
|---|---|---|---|---|---|---|
| **Random Forest (Baseline)** | **66.67%** | **0.5000** | **0.6667** | **0.5556** | 0.0000 | 0.0346 s |
| **Decision Tree** | 0.00% | 0.0000 | 0.0000 | 0.0000 | 0.1333 | 0.0002 s |
| **K-Nearest Neighbors (KNN)** | 0.00% | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0003 s |
| **Support Vector Machine (SVM)** | 33.33% | 0.1111 | 0.3333 | 0.1667 | 0.0000 | 0.0005 s |
| **Gradient Boosting** | 33.33% | 0.1111 | 0.3333 | 0.1667 | 0.1333 | 0.0260 s |

### Hyperparameter Tuning (Phase 8):
Validation search selected:
- `n_estimators`: 50
- `max_depth`: 3
- `min_samples_split`: 2
- `max_features`: "sqrt"

### Final Model Test Set Performance:
- **Test Accuracy**: **66.67%**
- **Macro Precision**: 0.5000
- **Macro Recall**: 0.6667
- **Macro F1-Score**: 0.5556
- **Multiclass One-vs-Rest ROC-AUC**:
  - **Macro-Average ROC-AUC**: **1.0000**
  - **Normal AUC**: **1.0000**
  - **Hemiplegic AUC**: **1.0000**
  - **Diplegic AUC**: **1.0000**
- Artifacts:
  - Model: [`models/gait_final_model.joblib`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/models/gait_final_model.joblib)
  - Preprocessor: [`models/gait_preprocessor.joblib`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/models/gait_preprocessor.joblib)
  - Metrics: [`reports/final_metrics.json`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/reports/final_metrics.json)
  - Confusion Matrix: [`reports/final_confusion_matrix.png`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/reports/final_confusion_matrix.png)
  - Multiclass ROC Curves: [`reports/final_roc_curves.png`](file:///Users/hkmac/child%20chain%20bait%20/ml-service/reports/final_roc_curves.png)

---

## 6. How to Reproduce

```bash
# 1. Extract raw C3D trials to feature CSV
python3 ml-service/src/extract_features.py

# 2. Run participant split, baseline training, comparison, and tuning
python3 ml-service/src/run_real_pipeline.py

# 3. Start the FastAPI service
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ⚕️ Medical Disclaimer
*This system is an academic machine-learning research prototype. It does not replace professional medical diagnosis, clinical assessment, or treatment by a qualified pediatric neurologist, physical therapist, or orthopedic physician.*
