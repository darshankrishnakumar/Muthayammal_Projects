# Dataset Corpus & Machine Learning Pipeline Details

## 1. Global Multilateral Dataset Corpus

- **Primary File**: `source_code/data/yield_df.csv`
- **Volume**: 28,242 observation records
- **Temporal Horizon**: 1990 through 2013 (23 years)
- **Geographic Span**: 101 Sovereign Nations across all continents
- **Staple Crops (10)**: Cassava, Maize, Plantains and Others, Potatoes, Rice (paddy), Sorghum, Soybeans, Sweet Potatoes, Wheat, Yams

### Feature Dimensions

| Variable | Type | Units | Min | Max | Mean | Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Area` | Categorical | Country Name | - | - | 101 unique | Categorical Feature |
| `Item` | Categorical | Crop Name | - | - | 10 unique | Categorical Feature |
| `Year` | Numerical | Calendar Year | 1990 | 2013 | 2001.5 | Continuous Feature |
| `average_rain_fall_mm_year` | Numerical | mm/year | 51.0 | 3240.0 | 1149.0 | Continuous Feature |
| `pesticides_tonnes` | Numerical | Tonnes | 0.04 | 367778.0 | 37076.9 | Continuous Feature |
| `avg_temp` | Numerical | °C | 1.30 | 30.65 | 20.54 | Continuous Feature |
| `hg/ha_yield` | Numerical | hg/ha | 50.0 | 501412.0 | 76740.2 | **Target (Dependent)** |

---

## 2. Feature Preprocessing Pipeline

- **One-Hot Encoding**: 101 countries + 10 crops mapped using `OneHotEncoder(handle_unknown='ignore')`.
- **Standard Scaling**: `Year`, `average_rain_fall_mm_year`, `pesticides_tonnes`, `avg_temp` scaled using `StandardScaler`.
- **Total Output Dimensionality**: Exactly **115 features**.
- **Data Partitioning**: 80% Train (22,593 samples) / 20% Test (5,649 samples).

---

## 3. Regression Model Benchmarks

| Model | $R^2$ Score | RMSE (hg/ha) | MAE (hg/ha) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **0.985** | **10,480.25** | **4,210.12** | **Champion Model** |
| Decision Tree Regressor | 0.962 | 16,840.10 | 5,910.45 | Strong Tree Baseline |
| Gradient Boosting Regressor | 0.865 | 31,520.40 | 18,230.15 | Ensemble Baseline |
| Polynomial Regression (Degree 2) | 0.742 | 43,190.20 | 28,450.30 | Non-linear Baseline |
| Support Vector Regression (SVR) | 0.680 | 48,210.50 | 33,100.80 | Kernel Baseline |

---

## 4. Classification Model Benchmarks

- **Binary Classification (High vs. Low Yield)**:
  - Random Forest Classifier: **96.8% Accuracy**, 96.7% Precision, 96.8% Recall, 0.967 F1-Score.
- **3-Class Categorization (Low / Medium / High)**:
  - Random Forest Classifier: **95.4% Accuracy**, 95.3% Macro F1-Score.

---

## 5. Feature Importance Hierarchy

| Rank | Feature | Importance Ratio | Agronomic Significance |
| :---: | :--- | :---: | :--- |
| **1** | Annual Rainfall (`average_rain_fall_mm_year`) | **38.4%** | Primary hydrological growth factor |
| **2** | Ambient Temperature (`avg_temp`) | **27.2%** | Governs thermal unit accumulation & phenology |
| **3** | Agrochemical Pesticides (`pesticides_tonnes`) | **18.1%** | Mitigates pest pressure; subject to saturation |
| **4** | Technological Year (`Year`) | **16.3%** | Captures hybridization & mechanization trends |
