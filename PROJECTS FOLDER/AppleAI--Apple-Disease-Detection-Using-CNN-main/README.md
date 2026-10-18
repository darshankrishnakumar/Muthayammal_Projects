# 🍎 Apple Health Intelligence AI — Pomological & Foliar Diagnostic Suite

An end-to-end Computer Vision and Deep Learning web application for real-time apple fruit condition detection and apple foliar disease diagnosis, powered by PyTorch, MobileNetV2 transfer learning, Grad-CAM visual explainability, and SQLite audit logging.

---

## 🌟 Key Capabilities

1. **Apple Fruit Condition Classifier (Model A):**
   - Classes: `Fresh` vs. `Rotten`
   - High-confidence post-harvest apple fruit inspection.
2. **Apple Leaf Disease Classifier (Model B):**
   - Classes: `Healthy`, `Apple_Scab`, `Black_Rot`, `Cedar_Apple_Rust`
   - Trained on pathologist-verified PlantVillage specimens.
3. **Automated Specimen Routing & Validator (Model C):**
   - Automatically determines whether an uploaded photo is an `apple_fruit` or `apple_leaf`.
   - Prevents cross-contamination: leaves are never diagnosed as Fresh/Rotten, and fruits are never diagnosed as foliar rust.
4. **Grad-CAM Explainability:**
   - Overlays high-resolution thermal heatmaps showing the exact regions the CNN focused on to make its diagnosis.
5. **Safety Uncertainty Rejection:**
   - Rejects non-apple images or predictions with low confidence (<60%) with actionable advisories instead of guessing.
6. **Integrated SQLite Database:**
   - Automatically logs all diagnostic transactions, timestamps, confidence scores, and severity grades to `apple_diagnostics.db`.
7. **Daylight Botanical UI Theme:**
   - Responsive web interface with 1-click authentic demonstration presets, webcam capture, and treatment recommendations.

---

## 🚀 Quick Start (Run in 1 Command)

### 1. Requirements
Ensure you have Python 3.10+ (tested with Python 3.11). Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://localhost:5003`** (or `http://127.0.0.1:5003`)

---

## 🧪 Command-Line Diagnostic & Inference Tools

### Predict Apple Fruit Condition:
```bash
python scripts/predict_fruit_condition.py sample_images/rot_apple_sample.jpg --save_cam results/fruit_cam.jpg
```

### Predict Apple Leaf Disease:
```bash
python scripts/predict_leaf_disease.py sample_images/scab_leaf_sample.jpg --save_cam results/leaf_cam.jpg
```

---

## 🗄️ Database Endpoints

* **Check Database Connection & Statistics:**
  ```bash
  curl http://localhost:5003/api/db/status
  ```
* **Retrieve Recent Diagnosis History:**
  ```bash
  curl http://localhost:5003/api/db/history?limit=10
  ```
* **System Health Check:**
  ```bash
  curl http://localhost:5003/health
  ```

---

## 📊 Run Automated Test Suite
To verify the entire pipeline (models, preprocessing, routing, Grad-CAM, database):
```bash
python tests/test_pipeline.py
```
*(All 24 automated unit and integration tests pass with 0 errors)*

---

## 📂 Project Directory Structure

```
├── app.py                      # Flask web application & REST API
├── apple_cnn_engine.py         # Multi-model PyTorch inference & Grad-CAM engine
├── database.py                 # SQLite database integration & query helpers
├── apple_diagnostics.db        # Persistent SQLite database file
├── requirements.txt            # Python dependencies
├── models/                     # Trained versioned PyTorch checkpoints (.pth & configs)
│   ├── apple_fruit_condition_v1.pth
│   ├── apple_fruit_condition_v1_config.json
│   ├── apple_leaf_disease_v1.pth
│   └── apple_leaf_disease_v1_config.json
├── sample_images/              # Preset authentic test images
├── scripts/                    # Training, dataset acquisition, audit & evaluation scripts
│   ├── acquire_leaf_dataset.py
│   ├── audit_dataset.py
│   ├── prepare_datasets.py
│   ├── train_model.py
│   ├── evaluate_models.py
│   ├── predict_fruit_condition.py
│   └── predict_leaf_disease.py
├── static/                     # CSS stylesheets & frontend JavaScript
├── templates/                  # HTML templates
├── tests/                      # Automated unit and integration test suite
└── results/                    # Confusion matrices, dataset audits & evaluation reports
```
