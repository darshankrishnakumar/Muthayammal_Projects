# AppleAI Codebase & Model Architecture Audit Report

**Date:** 2026-10-11  
**Project:** Apple Health Intelligence AI (Apple Disease Detection Using CNN)  
**Author:** Senior Machine Learning Engineer & Systems Architect  

---

## 1. System & Hardware Environment Audit

- **Operating System:** Windows 11 (PowerShell environment)
- **CPU:** 14 logical cores
- **RAM:** 15.43 GB total
- **GPU / Accelerator:** CPU only (`torch.cuda.is_available() == False`, PyTorch `2.14.0+cpu`)
- **Python Version:** Python 3.14.6
- **Existing Storage:** ~361 GB free disk space

---

## 2. Checkpoint & Model Architecture Audit

### 2.1 Checkpoint Analysis (`apple_cnn_model.pth` and `apple_cnn_model_v2.pth`)
- **`apple_cnn_model.pth` (28.98 MB):**
  - Contains keys `['custom_model', 'transfer_model']`
  - Classifier head: `classifier.4.weight` shape is `[4, 256]` (original 4 classes: Apple Scab, Black Rot, Cedar Rust, Healthy).
- **`apple_cnn_model_v2.pth` (28.99 MB):**
  - Contains keys `['custom_model', 'transfer_model']`
  - Classifier head: `classifier.4.weight` shape is `[5, 256]` (extended 5 classes including Apple Blotch).

### 2.2 Provenance of Existing Weights (`_calibrate_quick()`)
- In `apple_cnn_engine.py` (lines 327–403), the checkpoint creation is managed by `_calibrate_quick()`.
- **Finding:** The model checkpoint was **not** produced by training across thousands of balanced orchard/field images. Instead:
  1. It extracted 8 reference images from `sample_images/` (`scab_apple_sample.jpg`, `rot_apple_sample.jpg`, `normal_apple_sample.jpg`, `blotch_apple_sample.jpg`, `cedar_rust_sample.jpg`, `scab_leaf_sample.jpg`, `black_rot_leaf_sample.jpg`, `healthy_leaf_sample.jpg`).
  2. Applied simple crops and 2 augmentations per sample (~24 total image tensors).
  3. Optimized only the linear classification heads for 8–10 epochs in under 2 seconds.
- **Root Cause of Real-World Failure:** 
  The feature extractors have never seen true distribution variations (different apple cultivars, natural rot stages like soft brown decay or bitter rot, varying light, orchard backgrounds, supermarket stickers, blemishes). When any real-world apple is passed, activations fire unpredictably and the softmax head outputs confident but incorrect classes.

---

## 3. Pathology Label Mismatch (Foliar vs. Pomological Confusion)

The current 5-class target list is:
```
['Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy_Apple', 'Apple_Blotch']
```
- **Foliar vs. Fruit Mixing:**
  - `Cedar_Apple_Rust` is overwhelmingly an apple leaf disease (spotted orange-yellow foliar lesions); it rarely presents on commercial fruit in this form.
  - `Apple_Scab` appears differently on leaves (velvety olive soot) than on fruit (corky scabby lesions and cracking).
  - `Black_Rot` leaf symptoms are "Frog-Eye" spots, whereas fruit symptoms are concentric rotting rings and mummification.
- Attempting to force both fruit conditions and leaf pathologies into a single 5-class classifier causes high feature ambiguity and confusion.

---

## 4. Current Inference & Application Architecture

- **Backend:** Flask (`app.py`), running on port 5003.
- **Routes:**
  - `GET /`: Serves web dashboard (`index.html`)
  - `GET /health`: System status, supported classes
  - `GET /api/samples`: Sample thumbnails in base64
  - `POST /api/predict`: Handles JSON base64, multipart file upload, or preset sample IDs; invokes `engine.predict()`
  - `GET /api/benchmarks`: Benchmark comparison data
  - `GET /api/encyclopedia`: Pathology and treatment suggestions
- **Frontend:** Modular single-page dashboard with glassmorphism styling (`style.css`), live tabs, drag-and-drop file upload, field webcam capture, Grad-CAM slider, and intermediate layer activation visualizations.

---

## 5. Architectural Upgrade Plan

| Phase | Milestone | Deliverable |
| :--- | :--- | :--- |
| **Phase 2** | Model Separation | Separate Model A (Fruit: Fresh vs. Rotten), Model B (Leaf: Healthy, Scab, Black Rot, Rust), and Model C (Input Validator: Fruit vs. Leaf vs. Unsupported). |
| **Phase 3** | Dataset Pipeline | Standalone scripts to download, verify, clean, stratify, and audit datasets (Kaggle Rotten/Fresh Fruits, PlantVillage Apple Leaves, Fruits-360). |
| **Phase 4 & 5**| Generalization & Training | Modular PyTorch pipelines with data augmentations, MobileNetV2 ImageNet backbone, frozen $\to$ unfreeze fine-tuning, AdamW, early stopping, and metadata JSON saving. |
| **Phase 6** | Evaluation & Reporting | Held-out test evaluation generating accuracy, precision, recall, F1, confusion matrices, and misclassification error analysis. |
| **Phase 7** | Uncertainty & OOD Rejection | Rejection logic based on entropy and confidence thresholds to prevent arbitrary non-apple images from receiving false diagnoses. |
| **Phase 8** | Grad-CAM & XAI | Update Grad-CAM backward hook targeting for task-specific models and keep feature map visualizations intact. |
| **Phase 9 & 10**| Integration & Versioning | Update `apple_cnn_engine.py` and `app.py` with versioned `models/` checkpoints, backwards-compatible API schemas, and rollback safety. |
| **Phase 11 & 12**| Automated Tests & Delivery | Automated unit & integration tests (`tests/test_pipeline.py`), documentation, requirements, and instructions. |
