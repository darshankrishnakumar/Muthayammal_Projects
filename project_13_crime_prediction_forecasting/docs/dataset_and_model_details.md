# Dataset Corpus & Model Specifications

## 1. Dataset Overview

- **Source File**: `source_code/data/urban_crime_incidents.csv`
- **Total Records**: 5,000 incident events spanning 12 calendar months.
- **Police Districts**: 8 sectors (Central Downtown, North Waterfront, South Industrial, Westside Residential, East Commercial, Uptown Arts, Harbor District, Tech Corridor).
- **Features (11 Dimensions)**:
  1. `hour`: Hour of day (0-23)
  2. `day_of_week`: Day index (0=Monday to 6=Sunday)
  3. `month`: Calendar month (1-12)
  4. `is_weekend`: Binary flag (1 for Fri-Sun, 0 for Mon-Thu)
  5. `district`: Categorical police sector
  6. `location_type`: Environmental setting
  7. `historical_density`: Moving density metric (0.0 to 10.0)
  8. `ambient_light`: Illumination rating (1 to 5)
  9. `patrol_score`: Officer presence rating (1 to 5)
  10. `latitude`: Geographic latitude
  11. `longitude`: Geographic longitude

## 2. Model Specifications

### 2.1 Deep Neural Network (CrimeRiskDNN)
- **Framework**: PyTorch 2.14
- **Layers**: Linear(11->128) -> BatchNorm1d -> ReLU -> Dropout(0.25) -> Linear(128->64) -> BatchNorm1d -> ReLU -> Dropout(0.20) -> Linear(64->32) -> ReLU -> Linear(32->4)
- **Accuracy**: 68.30% (4-class risk classification)
- **F1 Score**: 0.6672 (weighted)
- **Weights File**: `source_code/models/crime_risk_dnn.pt`

### 2.2 Random Forest Classifier
- **Framework**: Scikit-Learn 1.6
- **Estimators**: 150 Decision Trees (max_depth=12)
- **Classes**: 8 Crime Categories
- **Accuracy**: 41.50% top-1 fine-grained accuracy
- **Artifacts File**: `source_code/models/crime_pipeline_artifacts.joblib`
