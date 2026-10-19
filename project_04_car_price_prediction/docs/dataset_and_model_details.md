# Dataset and Model Details

## 1. Historical Used Car Sales Dataset

The regression models are trained and benchmarked on a curated repository of 450 verified pre-owned car sales transactions (`source_code/data/car_data.csv`).

### Dataset Dimensions & Schema

| Column Name | Type | Description | Range / Values |
|---|---|---|---|
| `Car_Name` | String | Vehicle make, model, and trim | 'ritz', 'sx4', 'city', 'innova', 'fortuner' |
| `Year` | Integer | Year of vehicle manufacturing | 2003 – 2018 |
| `Selling_Price` | Float | Historical actual sale price in ₹ Lakhs (Target) | ₹0.35L – ₹35.0L (Mean: ₹4.66L) |
| `Present_Price` | Float | Original ex-showroom price when brand new (₹ Lakhs) | ₹0.5L – ₹92.6L (Mean: ₹7.63L) |
| `Kms_Driven` | Integer | Total odometer distance accumulated | 500 – 500,000 km (Mean: 36,947 km) |
| `Fuel_Type` | String | Powertrain category | Petrol (78.3%), Diesel (20.3%), CNG (1.4%) |
| `Seller_Type` | String | Commercial sales channel | Dealer (64.8%), Individual (35.2%) |
| `Transmission` | String | Gearbox configuration | Manual (86.4%), Automatic (13.6%) |
| `Owner` | Integer | Previous registered title transfers | 0 (First owner), 1, 2, 3+ |

---

## 2. Feature Engineering Pipeline

Raw tabular features undergo transformation using Scikit-Learn's `ColumnTransformer`:

1. **Derived Feature - Vehicle Age**:
   $$\text{Car\_Age} = 2024 - \text{Year}$$
2. **Derived Feature - Manufacturer Brand**:
   Extracted from the leading token of `Car_Name` (e.g., 'Maruti', 'Hyundai', 'Honda', 'Toyota', 'BMW').
3. **Continuous Scaling**:
   `StandardScaler` applied to `[Car_Age, Present_Price, Kms_Driven, Owner]` to center data ($\mu = 0$, $\sigma = 1$).
4. **Categorical Encoding**:
   `OneHotEncoder(handle_unknown='ignore')` applied to `[Fuel_Type, Seller_Type, Transmission, Brand]`, expanding features into a 22-dimensional space.

---

## 3. Comparative Model Evaluation Benchmarks

All models were evaluated on the held-out 20% test partition (90 vehicles) with fixed `random_state=42`:

| Model Architecture | Train $R^2$ | Test $R^2$ | Test RMSE (Lakhs) | Test MAE (Lakhs) | Generalization Gap | Status |
|---|---|---|---|---|---|---|
| **Random Forest Regressor** | **0.9922** | **0.9723** | **₹1.3989L** | **₹0.8835L** | **0.0199** | **Production Best** |
| **Decision Tree Regressor** | 0.9910 | 0.9525 | ₹1.8307L | ₹1.1746L | 0.0385 | Benchmark |
| **Linear Regression (OLS)** | 0.8856 | 0.8968 | ₹2.6989L | ₹1.7214L | -0.0112 | Baseline |

### Key Observations:
- **Ensemble Advantage**: Random Forest reduces Root Mean Squared Error by 48.2% relative to Ordinary Least Squares, demonstrating that non-linear interaction terms between age and showroom price are critical.
- **Minimal Overfitting**: The generalization gap between train $R^2$ (0.9922) and test $R^2$ (0.9723) is under 2%, proving exceptional generalization.

---

## 4. Feature Importance Hierarchy

Extracted from the 150-tree Random Forest regressor via Mean Decrease in Impurity (Gini Importance):

1. **Showroom Price (`Present_Price`)**: **75.14%**
2. **Vehicle Age (`Car_Age`)**: **13.30%**
3. **Odometer Mileage (`Kms_Driven`)**: **9.31%**
4. **Manufacturer Brand (`Brand`)**: **1.32%**
5. **Previous Owners (`Owner`)**: **0.33%**
6. **Seller Channel (`Seller_Type`)**: **0.20%**
7. **Transmission (`Transmission`)**: **0.20%**
8. **Fuel Powertrain (`Fuel_Type`)**: **0.20%**
