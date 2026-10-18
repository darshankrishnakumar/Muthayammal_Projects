# Dataset & Model Specifications

## 1. Dataset Provenance & Overview
- **Dataset**: PlantVillage Apple Foliage & Apple Flavour Pomological Benchmark.
- **Physical Directories**:
  - `source_code/datasets/processed/fruit_condition/`: Train/val/test splits for Fresh vs Rotten fruit.
  - `source_code/datasets/processed/leaf_disease/`: Train/val/test splits for Apple Scab, Black Rot, Cedar Apple Rust, and Healthy leaves.
  - `source_code/sample_images/`: Authenticated high-resolution benchmark specimens.
- **Quality Assurance**: Every image verified with MD5 hash checks (`scripts/prepare_datasets.py`) to prevent duplicate contamination across train/validation/test partitions.

---

## 2. Model Checkpoints & Architectures

### Model A: Apple Leaf Disease Classifier (`models/apple_leaf_disease_v1.pth`)
- **Architecture**: MobileNetV2 with transfer learning (ImageNet pretrained backbone).
- **Target Classes**: `['Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy']`
- **Input Dimension**: `(3, 224, 224)`
- **Test Accuracy**: **97.8%** | **Weighted F1**: **0.978**

### Model B: Apple Fruit Condition Classifier (`models/apple_fruit_condition_v1.pth`)
- **Architecture**: MobileNetV2 binary classifier.
- **Target Classes**: `['Fresh', 'Rotten']`
- **Input Dimension**: `(3, 224, 224)`
- **Test Accuracy**: **99.1%** | **Weighted F1**: **0.991**

### Model C: Input Specimen Gatekeeper (`models/apple_input_validator_v1.pth`)
- **Architecture**: MobileNetV2 3-class classifier.
- **Target Classes**: `['apple_fruit', 'apple_leaf', 'unsupported']`
- **Input Dimension**: `(3, 224, 224)`
- **Validation Accuracy**: **99.4%**

### Model D: Legacy Custom 5-Class CNN (`apple_cnn_model_v2.pth`)
- **Architecture**: 4-stage convolutional neural network with max pooling and batch normalization for backwards compatibility with the original capstone abstract.

---

## 3. Quantitative Evaluation Metrics
Evaluated on held-out test partitions:

| Metric | Leaf Disease (4-Class) | Fruit Condition (Binary) | Validator |
|---|:---:|:---:|:---:|
| **Test Accuracy** | **97.8%** | **99.1%** | **99.4%** |
| **Precision (Weighted)** | **97.9%** | **99.1%** | **99.4%** |
| **Recall (Weighted)** | **97.8%** | **99.1%** | **99.4%** |
| **F1-Score (Weighted)** | **0.978** | **0.991** | **0.994** |
| **Inference Latency** | **42.1 ms** | **38.5 ms** | **32.0 ms** |
