# Dataset & Model Specifications

## 1. Dataset Provenance & Overview
- **Dataset**: NSL-KDD Network Intrusion Detection Benchmark (University of New Brunswick / DARPA).
- **Physical Files**:
  - Raw: `source_code/datasets/KDDTest+.txt`
  - Cleaned & Structured: `source_code/datasets/nsl_kdd_clean.csv`
- **Total Records**: 22,544 full connection records.
- **Class Breakdown**:
  - `Normal`: 9,711 records (43.1%)
  - `DoS`: 7,458 records (33.1%)
  - `R2L`: 2,885 records (12.8%)
  - `Probe`: 2,421 records (10.7%)
  - `U2R`: 67 records (0.3%)
  - `Other_Attack`: 2 records

---

## 2. Feature Pipeline & Transformation
Inputs are processed through a fitted `ColumnTransformer` saved at `source_code/models/nsl_preprocessor.joblib`:
1. **Numerical Features (StandardScaler)**:
   - 34 continuous attributes including `duration`, `src_bytes`, `dst_bytes`, `count`, `srv_count`, `serror_rate`, `rerror_rate`, `same_srv_rate`, `diff_srv_rate`, `dst_host_count`, `dst_host_srv_count`, etc.
2. **Categorical Features (OneHotEncoder, `handle_unknown='ignore'`)**:
   - `protocol_type` (tcp, udp, icmp)
   - `service` (70 network services)
   - `flag` (11 TCP connection status flags)
3. **Total Feature Space**: Transformed to $\mathbf{x} \in \mathbb{R}^{111}$.

---

## 3. Supervised Ensemble Model Architectures

### Random Forest Classifier (`rf_nids_classifier.joblib`, 7.5 MB)
- `n_estimators`: 100
- `max_depth`: 16
- `criterion`: Gini impurity
- `random_state`: 42
- `n_jobs`: -1 (Parallel tree evaluation)

### Extra Trees Classifier (`et_nids_classifier.joblib`, 9.3 MB)
- `n_estimators`: 100
- `max_depth`: 16
- `criterion`: Gini impurity
- `random_state`: 42
- `n_jobs`: -1

---

## 4. Unsupervised Anomaly Model Architecture

### Isolation Forest (`isolation_forest_anomaly.joblib`, 889 KB)
- `n_estimators`: 100
- `contamination`: 0.18
- `random_state`: 42
- Path length anomaly metric: $s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$.

---

## 5. Quantitative Evaluation Metrics
Evaluated on a held-out test split of 4,509 connection records:

| Metric | Random Forest | Extra Trees | Hybrid Ensemble |
|---|:---:|:---:|:---:|
| **Test Accuracy** | **98.34%** | 98.03% | **98.41%** |
| **Weighted F1-Score** | **0.9833** | 0.9800 | **0.9840** |
| **Macro F1-Score** | **0.7812** | 0.7745 | **0.7850** |
| **Normal Precision** | **98.5%** | 98.1% | **98.6%** |
| **DoS Precision** | **98.4%** | 98.2% | **98.5%** |
| **Probe Precision** | **97.2%** | 96.9% | **97.4%** |
| **R2L Precision** | **96.8%** | 96.4% | **97.0%** |
| **Average Latency** | **42.5 ms** | 38.2 ms | **55.8 ms** |
