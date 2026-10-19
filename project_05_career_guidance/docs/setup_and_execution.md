# Setup and Execution Guide - Career Guidance AI

## System Prerequisites

- **Python**: 3.9+ (Tested on Python 3.10 and 3.12)
- **Node.js**: v18+ (Required only for Puppeteer automated walkthrough capture)
- **FFmpeg**: v5+ (Required for video encoding)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: ~500 MB disk space

---

## 1. Environment Installation

Navigate to the project root directory:

```bash
cd project_05_career_guidance/source_code
```

Install the project dependencies inside a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Key Python Dependencies
- `Flask>=3.0.0`
- `scikit-learn>=1.5.0`
- `xgboost>=2.0.0`
- `numpy>=1.24.0`
- `pandas>=2.0.0`
- `joblib>=1.3.0`
- `pytest>=8.0.0`

---

## 2. Model Training & Validation (Optional)

The pre-trained model cache is bundled at `source_code/model_cache.joblib`. To re-train or benchmark models on the 20,000 student dataset:

```bash
python3 train_models.py
```

This generates `model_cache.joblib` containing:
- Preprocessing pipelines (`LabelEncoder`, feature imputers)
- Trained `XGBClassifier`
- Trained `RandomForestClassifier` (50 estimators)
- Trained `DecisionTreeClassifier` (CART)
- Cross-validation performance dictionary

---

## 3. Running the Web Application

Launch the Flask server:

```bash
python3 app.py
```

By default, the server runs on port **5005**:
```
 * Running on http://127.0.0.1:5005
 * Ready for student assessment evaluations.
```

To run on a different port:
```bash
PORT=8080 python3 app.py
```

Open `http://127.0.0.1:5005` in any modern web browser (Chrome, Firefox, Safari, Edge).

---

## 4. Running the Automated Test Suite

Execute pytest across all unit, integration, and model inference test cases:

```bash
pytest test_model.py -v
```

Expected output:
```
test_model.py::test_dataset_exists PASSED
test_model.py::test_dataset_dimensions PASSED
test_model.py::test_engine_initialization PASSED
test_model.py::test_models_loaded PASSED
test_model.py::test_presets_available PASSED
test_model.py::test_fullstack_preset_prediction PASSED
test_model.py::test_cloud_devops_preset_prediction PASSED
test_model.py::test_cyber_security_preset_prediction PASSED
test_model.py::test_database_admin_preset_prediction PASSED
test_model.py::test_ui_ux_preset_prediction PASSED
test_model.py::test_top5_pathways_structure PASSED
test_model.py::test_radar_vector_generation PASSED
test_model.py::test_database_persistence PASSED
test_model.py::test_database_history_retrieval PASSED
test_model.py::test_api_health_endpoint PASSED
test_model.py::test_api_presets_endpoint PASSED
test_model.py::test_api_metrics_endpoint PASSED
test_model.py::test_api_predict_endpoint PASSED

============================== 18 passed in 1.04s ==============================
```

---

## 5. Capturing Automated UI Demonstrations

To reproduce the automated 3-minute video walkthrough:

```bash
# Ensure Flask server is running on port 5005
node scripts/recording/record_project_05.js
```

The compiled video will be saved to `walkthrough/walkthrough_video.mp4`.
