# Crop Yield Prediction Using Machine Learning Algorithms

**A Machine Learning Decision Support System & Harvest Estimation Platform**

---

## 1. Project Overview & Objective

### Objective
Develop a supervised machine learning-based decision support application that predicts agricultural crop yield from climate and agricultural parameters (crop type, country/region, annual rainfall, average temperature, pesticide usage, and year). The system incorporates regression for continuous yield density forecasting, dual-paradigm classification for risk categorization, a farm-scale total harvest production calculator, a prescriptive crop recommendation engine, and persistent SQLite prediction history.

### Problem Statement
Agricultural yield prediction is critical for national food security, budget planning, commodity supply chain management, and risk mitigation against climate volatility. Estimating crop yields prior to harvest allows farmers and policymakers to optimize resource allocation (irrigation and pesticide application) and forecast production tonnage accurately.

### Practical Applications
- **Harvest Volume Estimation:** Pre-season forecasting of yield density (`hg/ha` and `tonnes/ha`) and total metric tonnage based on farm land size.
- **Risk Assessment:** Classifying yield outcomes into binary (Above / Below Average) and 3-class (Low / Medium / High) risk categories.
- **Prescriptive Analytics:** Recommending the highest-yielding crop varieties for a specific climate scenario.
- **Historical Auditability:** Storing and exporting prediction audits via an embedded SQLite database.

---

## 2. Technology Stack & Architecture

| Layer | Technologies Used | Description |
|---|---|---|
| **Primary Backend** | Python 3.8+, Flask, Flask-CORS | REST API serving JSON endpoints and static SPA assets |
| **Secondary Interface**| Streamlit | 10-section interactive research and exploratory application (`app.py`) |
| **Primary Frontend** | HTML5, Vanilla CSS, React 18 (CDN), Babel Standalone | Responsive Single-Page Application (SPA) with glassmorphic cards and live data hydration |
| **Visualization** | Chart.js 4.4, Matplotlib | Dynamic charts: feature importance, actual vs. predicted scatter, confusion matrices, and yield trends |
| **Machine Learning** | Scikit-learn, NumPy, Pandas, Joblib | 6 regression models, 4 classification models, preprocessing transformers, serialized pipeline cache |
| **Database Layer** | SQLite (`cropai_history.db`) | Embedded database storing prediction records, input parameters, and total harvest estimates |
| **Automated Testing** | Pytest | 28 automated integration and pipeline unit tests covering all routes, validations, and conversions |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  React 18 Single-Page Application (SPA) · Chart.js · Babel │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask REST API                          │
│   /api/predict  ·  /api/classify  ·  /api/recommend         │
│   /api/history  ·  /api/stats     ·  /api/models/*          │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐┌──────────────────────────────┐
│     Machine Learning Core    ││    Database & Persistence    │
│  • ColumnTransformer (115 f) ││  • SQLite: cropai_history.db │
│  • StandardScaler            ││  • Parameterized CRUD        │
│  • Random Forest (R²=0.989)  ││  • CSV Exporter              │
│  • Logistic Reg & Naïve Bayes││                              │
│  • Models Cache (Joblib)     ││                              │
└──────────────────────────────┘└──────────────────────────────┘
```

---

## 3. Dataset Description & Semantic Clarifications

### Source Files & Properties
The dataset is merged from four United Nations Food and Agriculture Organization (FAO) datasets spanning 1990 to 2013 (`data/yield_df.csv`):
- **Records:** 28,242 rows
- **Countries (`Area`):** 101 geographical nations
- **Crop Types (`Item`):** 10 staple crops (Cassava, Maize, Plantains, Potatoes, Rice paddy, Sorghum, Soybeans, Sweet potatoes, Wheat, Yams)
- **Missing Values:** 0 (clean dataset)

### Features

| Column Name | Type | Description | Unit / Range |
|---|---|---|---|
| `Area` | Categorical | Country name (101 unique countries) | Geographical entity |
| `Item` | Categorical | Crop type (10 unique crops) | Agricultural species |
| `Year` | Numerical | Year of observation | 1990 – 2013 |
| `average_rain_fall_mm_per_year` | Numerical | Average annual rainfall | 51.0 – 3,240.0 mm/yr |
| `pesticides_tonnes` | Numerical | Total pesticide usage | 0.04 – 367,778 tonnes |
| `avg_temp` | Numerical | Average ambient temperature | 1.3°C – 30.6°C |
| `hg/ha_yield` | Numerical | **Target:** Crop yield density | Hectograms per hectare |

> [!IMPORTANT]
> **Dataset `Area` vs. Cultivated Farm Size:**  
> In the FAO dataset, the column labeled `Area` represents the **Country name** (geographic region), not the individual farmer's plot size. To prevent confusion and fulfill agricultural decision requirements, the application separates national location from an explicit, optional **Cultivated Farm Land Area** input (measured in Hectares or Acres) to compute total harvest volume.

---

## 4. Mathematical Conversions & Formulas

### 1. Yield Density Conversion
The model outputs crop yield in hectograms per hectare (`hg/ha`). 1 metric tonne equals 10,000,000 hectograms:

$$\text{Yield (tonnes/ha)} = \frac{\text{Yield (hg/ha)}}{10{,}000{,}000}$$

### 2. Land Area Conversion
1 hectare is approximately 2.47105 acres:

$$\text{Farm Area (hectares)} = \begin{cases} \text{Farm Area}, & \text{if unit is hectares} \\ \frac{\text{Farm Area (acres)}}{2.47105}, & \text{if unit is acres} \end{cases}$$

### 3. Total Expected Harvest
$$\text{Total Harvest (metric tonnes)} = \text{Yield (tonnes/ha)} \times \text{Farm Area (hectares)}$$

---

## 5. Machine Learning Pipeline & Algorithms

### Preprocessing Pipeline
1. **One-Hot Encoding:** Applied to `Area` (101) and `Item` (10) categorical features via `OneHotEncoder(handle_unknown='ignore')`, expanding them into 111 binary features.
2. **Standard Scaling:** Applied strictly to the 4 numerical columns (`Year`, `rainfall`, `pesticides`, `avg_temp`) via `StandardScaler`, fit only on training splits to prevent data leakage.
3. **Total Feature Dimensionality:** 115 features fed into all models.

### Regression Benchmark (80/20 Train/Test Split)

| Algorithm | R² Score | MAE (hg/ha) | RMSE (hg/ha) | Status |
|---|---|---|---|---|
| **Random Forest Regressor** | **0.9888** | **3,494** | **9,143** | **Best Model** |
| Decision Tree Regressor | 0.9823 | 3,607 | 11,508 | Strong non-linear baseline |
| Gradient Boosting Regressor | 0.8718 | 19,912 | 30,952 | Ensemble boosting |
| Polynomial Regression (deg=3) | 0.7600 | 29,389 | 42,345 | Polynomial expansion |
| Polynomial Regression (deg=2) | 0.7598 | 29,369 | 42,364 | Quadratic expansion |
| Linear Regression | 0.7597 | 29,261 | 42,368 | Linear baseline |
| Baseline (Training Mean) | -0.0003 | 65,021 | 86,449 | Naive baseline |
| Support Vector Regression (SVR RBF) | -0.2121 | 58,168 | 95,162 | Poor fit on sparse OHE data |

### Classification Benchmark (75/25 Train/Test Split)
The project covers both Binary (Above / Below Average split at dataset mean 77,053 hg/ha) and 3-Class (Low < 33rd percentile, Medium 33rd–67th, High > 67th percentile):

| Algorithm | Binary Accuracy | Binary F1-Score | 3-Class Accuracy | 3-Class F1-Score |
|---|---|---|---|---|
| **Random Forest Classifier** | **98.90%** | **0.9838** | **96.76%** | **0.9676** |
| **K-Nearest Neighbors (k=5)** | 98.67% | 0.9805 | 95.41% | 0.9541 |
| **Logistic Regression** | 94.99% | 0.9257 | 83.87% | 0.8386 |
| **Gaussian Naïve Bayes** | 81.33% | 0.7641 | 61.62% | 0.5773 |

*All abstract-mandated algorithms (Random Forest, Logistic Regression, Naïve Bayes) are fully trained and integrated.*

---

## 6. REST API Endpoints

| Method | Endpoint | Description | Sample Parameters / Output |
|---|---|---|---|
| `GET` | `/` | Serves the primary web application | HTML SPA (`frontend/index.html`) |
| `GET` | `/api/stats` | Dataset statistics | `{records: 28242, countries: 101, crops: 10}` |
| `GET` | `/api/options` | Supported dropdown options | `{countries: [...], crops: [...]}` |
| `GET` | `/api/models/regression` | Regression benchmark metrics | `[{name, r2, mae, rmse, best}, ...]` |
| `GET` | `/api/classification` | Classifier cards & confusion matrices | `?type=binary` or `?type=3class` |
| `GET` | `/api/visualizations` | Real feature importances & scatter | `{featImportance: [...], scatter: [...]}` |
| `POST`| `/api/predict` | Predicts continuous yield & calculates harvest | Accepts JSON with `country`, `crop`, `year`, `rain`, `pest`, `temp`, optional `farm_area`, `farm_area_unit` |
| `POST`| `/api/classify` | Predicts binary or 3-class yield category | Accepts JSON with scenario parameters + `type` (`binary` / `3class`) |
| `POST`| `/api/recommend` | Prescriptive Crop Recommendation Engine | Evaluates all 10 crops, returns top 3 ranked crops by predicted yield |
| `GET` | `/api/history` | Retrieves persistent SQLite prediction history | `?limit=50` (or `?country=X&crop=Y` for dataset trend) |
| `GET` | `/api/history/<id>` | Retrieves single prediction details by ID | `{id: 1, country: "Albania", ...}` |
| `DELETE`| `/api/history/<id>`| Deletes specific prediction from database | `{success: true, message: "..."}` |
| `DELETE`| `/api/history` | Clears all persistent prediction history | `{success: true, message: "..."}` |
| `GET` | `/api/history/export` | Downloads history as CSV file | `cropai_history.csv` attachment |

---

## 7. Database Structure (`cropai_history.db`)

SQLite database table `prediction_history`:

```sql
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,           -- UTC Timestamp string
    task_type TEXT NOT NULL,           -- 'regression' | 'classification'
    country TEXT NOT NULL,             -- Selected country
    crop TEXT NOT NULL,                -- Selected crop
    year INTEGER NOT NULL,             -- Crop year
    rainfall REAL NOT NULL,            -- Annual rainfall (mm)
    pesticides REAL NOT NULL,          -- Pesticides used (tonnes)
    temperature REAL NOT NULL,         -- Average temperature (°C)
    model_name TEXT NOT NULL,          -- Algorithm used
    predicted_yield REAL,              -- Yield in hg/ha
    yield_unit TEXT,                   -- 'hg/ha'
    yield_tonnes_per_ha REAL,          -- Converted tonnes/ha
    farm_area REAL,                    -- Input land size
    farm_area_unit TEXT,               -- 'ha' or 'acres'
    farm_area_ha REAL,                 -- Normalized hectares
    total_harvest_tonnes REAL,         -- Estimated harvest in tonnes
    classification_label TEXT,         -- e.g. 'Above Average', 'High'
    classification_class INTEGER,      -- Discrete class (0, 1, 2)
    classification_type TEXT           -- 'binary' | '3class'
);
```

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.8 to 3.14
- Web browser (Chrome, Edge, Firefox, Safari)

### Step 1: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 2: Run the Web Application
Start the primary Flask REST + React application:
```bash
python backend_api.py
```
Open your browser at:
```
http://localhost:5000
```

*(Optional: The secondary research Streamlit app can be run with `streamlit run app.py` on port 8501).*

### Step 3: Run Automated Test Suite
Execute the full pytest suite:
```bash
python -m pytest -v
```
All 28 automated integration and unit tests will run and validate the REST endpoints, input boundary checks, farm size calculations, recommendation engine, and database persistence.

---

## 9. Usage Guide

### 1. Crop Yield & Total Harvest Prediction
1. Open the web app at `http://localhost:5000` and navigate to **Predictions**.
2. Select the **📈 Yield Prediction** tab.
3. Choose a Country and Crop, and enter the climate scenario (Rainfall, Pesticides, Temperature, Year).
4. *(Optional)* Enter your cultivated farm size in **Hectares** or **Acres** to calculate total expected harvest.
5. Click **Predict Yield & Harvest**.
6. View the predicted yield rate (`hg/ha` and `tonnes/ha`), total expected metric tonnage, confidence score, and historical trend comparison.
7. The result is automatically recorded in the persistent SQLite database.

### 2. Yield Classification (Risk Categorization)
1. Select the **🏷️ Classification** tab.
2. Choose between **Binary (Above / Below Average)** or **3-Class (Low / Medium / High)**.
3. Select an algorithm (e.g., *Random Forest Classifier*, *Logistic Regression*, or *Naïve Bayes*).
4. Click **Classify Yield Category**.

### 3. Prescriptive Crop Recommendation
1. Select the **🌱 Recommend Crop** tab.
2. Enter the climate parameters and country.
3. Click **Recommend Best Crops**.
4. The system evaluates all 10 staple crops and displays the **Top 3 Recommended Crops** ranked by predicted yield potential, alongside a comparative analysis.

### 4. Prediction History & CSV Export
1. Scroll down on the Predictions page to the **Persistent Prediction History (SQLite)** table.
2. Inspect past scenarios, timestamps, and harvest estimations.
3. Click **Export CSV** to download a spreadsheet report (`cropai_history.csv`) of all saved records.

---

## 10. Limitations & Future Scope
- **Temporal Horizon:** Training observations conclude in 2013; adding post-2013 satellite data would account for recent global climate anomalies.
- **Crop Variety:** The dataset tracks 10 major global crops; regional pulses, spices, and horticulture crops are not included in the FAO core series.
- **Soil & Fertilizer Parameters:** The FAO dataset lacks soil NPK values, pH, and micro-nutrients. Incorporating local soil health cards is a recommended extension for localized farm-gate deployments.
- **Economic Factors:** The crop recommendation engine ranks crops strictly by predicted agronomic yield density; market prices, operational labor costs, and storage logistics should be considered when selecting crops commercially.
