# Car Price Prediction System (Machine Learning Web Application)

A production-ready machine learning web application that predicts used car valuations based on historical vehicle features using trained regression models (**Random Forest Regressor**, **Decision Tree Regressor**, and **Linear Regression**).

---

## 🌟 Key Features

- **End-to-End Machine Learning Pipeline**: Preprocessing, outlier clipping, numerical scaling, categorical one-hot encoding, and automated best-model selection.
- **Multi-Algorithm Comparison**: Benchmarks Linear Regression, Decision Tree Regression, and Random Forest Regression with cross-validation on test sets.
- **High Predictive Accuracy**: Random Forest achieves **R² = 0.9716** with a low **RMSE of 1.41 Lakhs** and **MAE of 0.89 Lakhs**.
- **Full-Stack Web Interface**:
  - Interactive prediction interface with sliders, dropdowns, and instant valuation feedback.
  - Model algorithm selector allowing live side-by-side comparison of predictions.
  - Confidence interval estimation (90% range) and vehicle depreciation analytics.
  - Dataset sample explorer and live model performance metrics cards.
- **Dual Runtime Support**:
  - Pure Python (FastAPI + Uvicorn + Jinja2)
  - Full-stack modern web experience (React 19 + Tailwind CSS + Vite / Express bridge)

---

## 📁 Project Structure

```
├── app/
│   ├── main.py              # FastAPI application & prediction API endpoints
│   ├── static/              # CSS stylesheets and client assets
│   │   └── style.css
│   └── templates/           # Jinja2 HTML templates for pure Python UI
│       └── index.html
├── data/
│   └── car_data.csv         # Car dataset (Kaggle CarDekho benchmark)
├── models/
│   ├── best_car_price_model.joblib   # Top performing serialized model
│   ├── best_car_price_model.pkl      # Pickle serialized pipeline
│   ├── random_forest_regression.joblib
│   ├── decision_tree_regression.joblib
│   ├── linear_regression.joblib
│   ├── model_metadata.json  # Feature definitions and evaluation metrics
│   └── training.log         # Detailed model training logs
├── notebooks/
│   └── car_price_analysis_and_modeling.ipynb # EDA and modeling notebook
├── scripts/
│   ├── prepare_dataset.py   # Dataset generation & cleaning script
│   └── train_model.py       # Full training, evaluation & serialization pipeline
├── src/                     # Modern interactive React dashboard
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── requirements.txt         # Python dependencies
├── package.json             # Web application configuration
└── README.md                # Project documentation
```

---

## 📊 Dataset & Features

Based on the standard **CarDekho / Kaggle Car Price Dataset**:

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `Car_Name` | String | Make and model of the car (e.g., Maruti Swift, Toyota Fortuner, Honda City) |
| `Year` | Integer | Manufacturing year (2008 - 2024) |
| `Present_Price` | Float | Original ex-showroom price in Lakhs (or $10,000s) |
| `Kms_Driven` | Integer | Total kilometers logged on odometer |
| `Fuel_Type` | Categorical | `Petrol`, `Diesel`, `CNG` |
| `Seller_Type` | Categorical | `Dealer`, `Individual` |
| `Transmission` | Categorical | `Manual`, `Automatic` |
| `Owner` | Integer | Number of prior owners (`0` = first owner, `1`, `2`, `3+`) |
| **`Selling_Price`** | **Target Float** | Actual sold market price in Lakhs |

### Preprocessing Steps
1. **Missing Value Imputation**: Median strategy for numerical columns (`Present_Price`, `Kms_Driven`); most-frequent mode strategy for categorical columns (`Fuel_Type`).
2. **Feature Engineering**: Derived `Car_Age = Current_Year - Year` and extracted primary `Brand` from vehicle names.
3. **Outlier Mitigation**: Capped extreme odometer values (`Kms_Driven`) at the 99th percentile to prevent heavy-tail distortion.
4. **Encoding & Scaling**: Scikit-Learn `ColumnTransformer` with `StandardScaler` for continuous features and `OneHotEncoder(handle_unknown='ignore')` for nominal categories.

---

## 📈 Model Evaluation & Benchmark Results

Evaluated on an independent 20% hold-out test set (90 test samples, 360 training samples):

| Algorithm | Test R² Score | RMSE | MAE | Rank |
| :--- | :---: | :---: | :---: | :---: |
| **Random Forest Regression** | **0.9716 (97.2%)** | **1.4157** | **0.8932** | 🥇 **Best** |
| **Decision Tree Regression** | **0.9525 (95.3%)** | **1.8307** | **1.1746** | 🥈 Runner-up |
| **Linear Regression** | **0.8968 (89.7%)** | **2.6991** | **1.7216** | 🥉 Baseline |

- **R² Score (Coefficient of Determination)**: Random Forest explains **97.2%** of price variance.
- **RMSE & MAE**: Average prediction error is under **0.89 Lakhs**, providing dependable resale valuation.

---

## 🚀 Getting Started

### 1. Installation

Clone repository and install Python requirements:
```bash
pip install -r requirements.txt
```

### 2. Retraining the ML Pipeline

To re-run data cleaning, train all 3 regression models, and export new model files & feature importances:
```bash
python scripts/train_model.py
```

### 3. Running Automated Tests

Run the comprehensive test suite verifying ML pipeline, API endpoints, boundary validation, and SQLite CRUD operations:
```bash
python tests/test_api_and_model.py
```

### 4. Running the Web Application

#### Option A: Run FastAPI Microservice & Automotive Portal (Port 5004)
```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 5004
```
Open your browser to `http://localhost:5004`.

#### Option B: Run Full-Stack Web Application (Node / React + Python)
```bash
npm run dev
```

---

## 📚 Technical Documentation Suite

Complete technical documentation is located in the `docs/` directory:
- [Architecture & Dataflow Design](docs/architecture.md)
- [Dataset & Model Benchmarks](docs/dataset_and_model_details.md)
- [REST API Reference](docs/api_documentation.md)
- [Setup & Execution Instructions](docs/setup_and_execution.md)
- [Automated Testing & Verification Report](docs/testing_report.md)
- [Limitations & Future Roadmap](docs/limitations_and_future_work.md)
- [Third-Party Notices](docs/third_party_notices.md)
- [Final Acceptance Sign-off Report](docs/acceptance_report.md)
- [Formal Academic Documentation (DOCX)](docs/technical_documentation.docx)
- [15-Slide Presentation Deck (PPTX)](presentations/project_presentation.pptx)
- [Walkthrough Video Demonstration](walkthrough/walkthrough_video.mp4)

---

## 💾 Database Architecture

- **Engine**: Embedded SQLite (`data/predictions.db`)
- **Table**: `prediction_history`
- **Fields**: `id`, `created_at`, `brand`, `car_model`, `year`, `age_years`, `present_price`, `kms_driven`, `fuel_type`, `transmission`, `seller_type`, `owner`, `algorithm`, `predicted_price_lakhs`, `predicted_price_usd`, `depreciation_percentage`, `retention_rating`, `lower_bound_lakhs`, `upper_bound_lakhs`
- **Zero Configuration**: Created and managed automatically by the backend with zero external setup.

---

## 🔌 API Reference

### `POST /api/predict`
Calculates vehicle market valuation and persists entry to SQLite history.
```json
{
  "brand": "Toyota",
  "car_model": "Fortuner",
  "year": 2019,
  "present_price": 35.5,
  "kms_driven": 62000,
  "fuel_type": "Diesel",
  "seller_type": "Dealer",
  "transmission": "Automatic",
  "owner": 0,
  "algorithm": "Random Forest Regression"
}
```

### `GET /api/history`
Returns persistent prediction history records from SQLite database.

### `DELETE /api/history/{id}`
Deletes a specific prediction record from history.

### `DELETE /api/history`
Clears all prediction history records.

### `GET /api/info`
Returns metadata, Random Forest feature importance weights, model options, and evaluation metrics for all 3 models.

### `GET /api/dataset/sample`
Returns historical car records from `data/car_data.csv` for exploration.

### `GET /api/health`
Health check endpoint reporting microservice status and loaded ML models.
