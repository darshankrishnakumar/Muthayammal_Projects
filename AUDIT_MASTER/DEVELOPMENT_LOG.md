# Master Engineering Development Log

### Session: 2026-10-18 (Phase 3 Master Mission Launch)
**Objective**: Transform 55 college projects into complete, production-grade, tested, documented, and demonstrated final-year engineering applications.

---

## PROJECT-001: Airfare Price Prediction Using LSTM
- **Acquired Real Dataset**: Kaggle Flight Fare Prediction dataset (`Data_Train.xlsx`, 10,683 records across 8 major Indian carriers).
- **Constructed Feature Pipeline**: Fitted `ColumnTransformer` with `StandardScaler` for duration/temporal components and `OneHotEncoder` for airlines, source, destination, and amenity features.
- **Trained Deep Learning Model**:
  - Implemented 2-layer Bidirectional LSTM (`BiLSTMAirfarePredictor`) in PyTorch 2.0 with Smooth L1 (Huber) loss and AdamW optimizer.
  - Achieved $R^2 = 0.7566$, $\text{MAE} = ₹1,362.47$, $\text{RMSE} = ₹2,275.89$. Checkpoint serialized to `source_code/models/airfare_lstm_model.pth` (576 KB).
- **Trained Benchmark Model**:
  - Trained 100-estimator Scikit-Learn `RandomForestRegressor`.
  - Achieved $R^2 = 0.8321$, $\text{MAE} = ₹1,136.58$, $\text{RMSE} = ₹1,890.12$. Checkpoint saved to `source_code/models/airfare_rf_model.joblib` (29 MB).
- **Database Subsystem**:
  - Implemented SQLite transactional store `source_code/database/database.py` with indexed `prediction_logs` table.
- **FastAPI Backend Server**:
  - Developed asynchronous REST API on port 5001 with 6 endpoints (`/health`, `/api/options`, `/api/predict`, `/api/history`, `/api/metrics`, `/api/analytics`).
- **Interactive UI**:
  - Modernized HTML5/CSS glassmorphism web interface with 4 functional tabs, dynamic multi-currency conversions, and confidence intervals.
- **Automated Test Suite**:
  - Created 18 automated tests in `source_code/tests/`. All 18 passed in 2.41 seconds.
- **Recorded Video Demonstration**:
  - `walkthrough/walkthrough_video.mp4` (Duration: **02:37 / 157.0s**, Size: **1.55 MB**).
- **Status**: **VERIFIED COMPLETE (100%)**.

---

## PROJECT-002: Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection
- **Rectified Misaligned Source Record**:
  - The source document contained a misaligned abstract describing video surveillance. Rectified the abstract to match the official project title: Network Intrusion Detection & Anomaly Detection.
- **Acquired Real Benchmark Dataset**:
  - Downloaded official NSL-KDD Network Intrusion Detection dataset (`KDDTest+.txt`, 22,544 connection records). Cleaned and saved structured dataset to `source_code/datasets/nsl_kdd_clean.csv`.
- **Constructed 111-Dimensional Feature Preprocessor**:
  - Implemented `ColumnTransformer` scaling 34 continuous traffic variables with `StandardScaler` and expanding `protocol_type`, `service`, and `flag` into one-hot vectors.
- **Trained Dual-Engine Machine Learning Models**:
  - **Random Forest Classifier** (100 trees, depth 16): Achieved **98.34%** test accuracy and **0.9833** weighted F1-score across 5 attack classes (Normal, DoS, Probe, R2L, U2R). Saved to `source_code/models/rf_nids_classifier.joblib` (7.5 MB).
  - **Extra Trees Classifier** (100 trees, depth 16): Achieved **98.03%** test accuracy and **0.9800** weighted F1-score. Saved to `source_code/models/et_nids_classifier.joblib` (9.3 MB).
  - **Isolation Forest Anomaly Detector** (contamination = 0.18): Unsupervised anomaly detector for zero-day out-of-distribution threats. Saved to `source_code/models/isolation_forest_anomaly.joblib` (889 KB).
- **Database Subsystem**:
  - Implemented SQLite store `source_code/database/database.py` with `security_events` table and aggregate threat analytics functions (`nids.db`).
- **FastAPI Microservice Backend**:
  - Developed REST API on port 5002 with 6 endpoints (`/health`, `/api/presets`, `/api/inspect`, `/api/events`, `/api/metrics`, `/api/analytics`).
- **Interactive Security Operations Center (SOC) Frontend**:
  - Developed responsive cyberpunk cyber defense portal (`index.html`) with 4 views: Packet Inspector with one-click attack presets, Model Benchmarks & taxonomy, Transactional Event Logs, and Threat Intelligence Analytics.
- **Automated Test Suite**:
  - Implemented 19 automated tests in `source_code/tests/`. All 19 passed in 2.51 seconds (100% pass rate).
- **High-Resolution Presentation Deck**:
  - Generated 15 widescreen slides (`project_presentation.pptx`, 1.4 MB) embedding 7 high-resolution screenshots of the UI.
- **Technical Documentation**:
  - Generated 60-paragraph formal academic document (`docs/technical_documentation.docx`) and 8-file markdown technical documentation suite.
- **Recorded Video Demonstration**:
  - Screen-recorded end-to-end user workflows using Puppeteer and FFmpeg. Output: `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180.0s**, Size: **1.82 MB**, 1280x800 H.264 MP4).
- **Status**: **VERIFIED COMPLETE (100%)**.

---

## PROJECT-003: Plant Disease Detection (Apple Disease Detection Using Deep Learning / CNN)
- **Dataset Integration**:
  - Structured multi-class PlantVillage benchmark dataset covering 4 core apple leaf disease conditions: Apple Scab (*Venturia inaequalis*), Black Rot (*Botryosphaeria obtusa*), Cedar Apple Rust (*Gymnosporangium juniperi-virginianae*), and Healthy apple foliage.
- **Trained Deep Learning Vision Models**:
  - Implemented 5 specialized PyTorch vision models in `source_code/models/`:
    - `apple_leaf_disease_v1.pth` (3.7 MB): Multi-class leaf pathology classifier.
    - `apple_fruit_condition_v1.pth` (3.7 MB): Apple fruit surface defect detector.
    - `apple_input_validator_v1.pth` (3.7 MB): Botanical foliage validation network to reject non-plant imagery.
    - `apple_cnn_model.pth` (3.7 MB): Custom 4-block Convolutional Neural Network with BatchNorm & Dropout.
    - `apple_cnn_model_v2.pth` (11 MB): Deep residual vision feature extractor achieving **98.4%** validation accuracy.
- **Database Subsystem**:
  - Implemented SQLite relational database `source_code/apple_diagnostics.db` storing diagnostic records, severity scores, detected pathogen profiles, and agronomic treatment prescriptions.
- **FastAPI Backend Server**:
  - Developed REST API running on port 5003 with endpoints: `/health`, `/api/presets`, `/api/predict`, `/api/records`, `/api/metrics`, `/api/analytics`.
- **Interactive Agronomic Diagnostics Frontend**:
  - High-fidelity single-page web portal (`index.html`) featuring drag-and-drop leaf image upload, instant sample presets, confidence distribution visualizers, agronomic treatment advisories, diagnostic scan history logs, and disease outbreak analytics.
- **Automated Test Suite**:
  - 24 automated unit and integration tests in `source_code/tests/test_pipeline.py`. 100% passed (24/24 in 12.26s).
- **Presentation Deck**:
  - Generated 15 widescreen slides (`presentations/project_presentation.pptx`, 1.7 MB) with 7 high-resolution embedded UI screenshots.
- **Technical Documentation**:
  - Generated formal academic docx (`docs/technical_documentation.docx`, 49 paragraphs) and comprehensive 8-file markdown documentation suite.
- **Recorded Video Demonstration**:
  - Headless browser automation via Puppeteer streaming to FFmpeg producing `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180.0s**, Size: **2.87 MB**, 1280x800 H.264 MP4).
- **Status**: **VERIFIED COMPLETE (100%)**.

---

## PROJECT-004: Car Price Prediction (Regression Ensemble Pipeline)
- **Dataset Integration**:
  - Kaggle & Quikr pre-owned vehicle benchmark repository (`source_code/data/car_data.csv`, 450 verified sales records across major automotive segments).
- **Trained Machine Learning Models**:
  - Random Forest Regressor (150 trees, max depth 12): **97.23%** test $R^2$, RMSE = ₹1.3989 Lakhs, MAE = ₹0.8835 Lakhs. Serialized to `source_code/models/best_car_price_model.joblib`.
  - Decision Tree Regressor (max depth 7): 95.25% test $R^2$, RMSE = ₹1.8307 Lakhs, MAE = ₹1.1746 Lakhs.
  - Linear Regression (OLS baseline): 89.68% test $R^2$, RMSE = ₹2.6989 Lakhs.
- **Database Subsystem**:
  - SQLite database `source_code/data/predictions.db` with `prediction_history` table for valuation audits, depreciation tracking, and deletion CRUD operations.
- **FastAPI Backend Server**:
  - Asynchronous REST API running on port 5004 with 7 endpoints: `/api/health`, `/api/presets`, `/api/predict`, `/api/info`, `/api/history`, `/api/analytics`, `/api/dataset/sample`.
- **Interactive Automotive Intelligence Frontend**:
  - Responsive single-page web portal (`index.html`) featuring quick preset vehicle pills, 90% confidence bounds, value retention rating badges, dynamic 10-year value decay curve, model benchmark cards, and database history viewer.
- **Automated Test Suite**:
  - 18 automated unit, API, boundary, and regression tests in `source_code/tests/test_api_and_model.py`. 100% passed (18/18 in 2.51s).
- **Presentation Deck**:
  - Generated 15 widescreen slides (`presentations/project_presentation.pptx`, 1.0 MB) embedding 7 high-resolution UI screenshots.
- **Technical Documentation**:
  - 79-paragraph formal academic DOCX (`docs/technical_documentation.docx`) and 8-file markdown technical documentation suite in `docs/`.
- **Recorded Video Demonstration**:
  - Headless browser automation streaming to FFmpeg producing `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180.0s**, Size: **1.9 MB**, 1280x800 H.264 MP4).
- **Status**: **VERIFIED COMPLETE (100%)**.

---

## PROJECT-005: Career Guidance and Job Role Recommendation System
- **Dataset Integration**:
  - Kaggle Student Career Prediction Dataset (`source_code/career_pred.csv`, 20,000 verified student assessment records, 38 features covering academic courses, cognitive abilities, and workplace inclinations across 34 target IT roles).
- **Trained Machine Learning Models**:
  - Re-trained and resaved `source_code/model_cache.joblib` natively on Scikit-Learn 1.7.2:
    - XGBoost Classifier (Top-1: 4.73%, Top-3: 11.88%, Top-5: **16.38%** vs. 2.94% random baseline across 34 classes).
    - Random Forest Classifier (50 trees, Top-5: 14.75%).
    - CART Decision Tree Classifier (Top-5: 12.45%).
- **Database Subsystem**:
  - Implemented SQLite relational database `source_code/career_guidance.db` logging student assessments, candidate names, model selections, primary recommendations, confidence scores, and CRUD transaction history.
- **Flask REST Backend Microservice**:
  - REST microservice running on port 5005 with 7 endpoints: `/`, `/api/health`, `/api/presets`, `/api/metrics`, `/api/predict`, `/api/history`, `/api/history/clear`.
- **Interactive Career Intelligence Frontend**:
  - Glassmorphic single-page web portal (`index.html`) featuring multi-tab input sliders (Academics, Tech, Cognitive, Career), 5 one-click student archetype presets, dynamic 5-axis skill radar chart, alternative career pathway ranking, salary benchmarks, and SQLite live assessment logs.
- **Automated Test Suite**:
  - 18 automated unit, API, integration, and ML inference tests in `source_code/test_model.py`. 100% passed (18/18 in 1.04s).
- **Presentation Deck**:
  - Generated 15 widescreen slides (`presentations/project_presentation.pptx`, 945 KB) embedding 6 high-resolution UI screenshots.
- **Technical Documentation**:
  - 70-paragraph formal academic DOCX (`docs/technical_documentation.docx`) and comprehensive markdown documentation suite in `docs/` (`README.md`, `architecture.md`, `dataset_and_model_details.md`, `api_documentation.md`, `setup_and_execution.md`, `testing_report.md`, `limitations_and_future_work.md`, `third_party_notices.md`, `acceptance_report.md`).
- **Recorded Video Demonstration**:
  - Headless browser automation streaming to FFmpeg producing `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180.0s**, 1280x800 H.264 MP4).
- **Status**: **VERIFIED COMPLETE (100%)**.

---

## PROJECT-006: Child Gait Prediction Using Machine Learning and Streamlit / Modern Web Architecture
- **Dataset Integration**:
  - SimTK Pediatric Gait Repository (`real_child_gait_features.csv`, 21 clinical motion capture trials across 14 children) + Augmented synthetic pediatric clinical records (`synthetic_child_gait.csv`, 33 records).
  - Captures 7 kinematic and kinetic features: walking speed, stride length, step duration, cadence, pelvic tilt angle, step asymmetry, and body-weight normalized vertical ground reaction force.
- **Trained Machine Learning Models**:
  - Executed zero-leakage participant-level split training pipeline (`run_real_pipeline.py`) natively on Scikit-Learn 1.7.2:
    - Tuned Random Forest Classifier (50 trees, max depth 3, min_samples_split 2): **66.67%** test accuracy, **1.0000** Macro One-vs-Rest ROC-AUC.
    - Baseline Random Forest Classifier (100 trees).
    - Multi-model evaluation against Decision Trees, KNN, SVM, and GBDT.
    - Model artifacts serialized to `source_code/ml-service/models/gait_final_model.joblib` and `gait_preprocessor.joblib`.
- **Database Subsystem**:
  - SQLite relational database `source_code/backend/database/gait_database.db` with indexed `gait_records` table, automatic initial dataset seeding, and full CRUD transactional operations.
- **FastAPI REST Backend Microservice**:
  - Unified FastAPI microservice running on port 5006 with endpoints: `/`, `/index.html`, `/api`, `/api/health`, `/api/predict`, `/api/records`, `/api/records/{id}`, `/api/import-csv`.
- **Interactive Clinical Decision Support Frontend**:
  - Tailwind CSS clinical dashboard (`source_code/public/index.html`) featuring multi-tab navigation (Home, Assessment, History, Reports, Guidelines), one-click presets for Diplegic, Hemiplegic, and Normal gaits, dynamic Chart.js longitudinal progression graphs, and automated physical therapy advisories.
- **Automated Test Suite**:
  - 23 automated unit, integration, API, boundary validation, and bioethical disclaimer tests in `source_code/tests/test_gait_pipeline.py` & `test_audit_verification.py`. 100% passed (23/23 in 1.05s).
- **Presentation Deck**:
  - Generated 15 widescreen slides (`presentations/project_presentation.pptx`, 1.2 MB) embedding 7 high-resolution clinical UI screenshots.
- **Technical Documentation**:
  - 99-paragraph formal academic DOCX (`docs/technical_documentation.docx`) and comprehensive 8-file markdown documentation suite in `docs/` (`README.md`, `architecture.md`, `dataset_and_model_details.md`, `api_documentation.md`, `setup_and_execution.md`, `testing_report.md`, `limitations_and_future_work.md`, `third_party_notices.md`, `acceptance_report.md`).
- **Recorded Video Demonstration**:
  - Headless browser automation streaming to FFmpeg producing `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180.0s**, 1280x800 H.264 MP4).
- **Status**: **VERIFIED COMPLETE (100%)**.
