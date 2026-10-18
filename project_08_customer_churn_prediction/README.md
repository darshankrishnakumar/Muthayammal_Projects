# Customer Churn Prediction System: Enterprise Architecture

A professional, full-stack, enterprise-grade **Customer Churn Prediction and Intelligence Platform** built with **React**, **Java Spring Boot**, **Python FastAPI**, **Scikit-learn**, and a **MySQL SQL Relational Database**.

---

## 🏛️ System Architecture

```
                      React Frontend (Port 3000)
             [Executive Dashboard | Predict | History | Metrics]
                                    |
                                    | HTTP REST API (/api/*)
                                    v
                 Java Spring Boot Backend (Port 8080)
   [Validation | Recommendation Engine | MySQL Persistence | Aggregator]
                                    |
                                    | HTTP REST API (/predict, /metrics, /health)
                                    v
                 Python ML Inference Service (Port 8000)
                       [FastAPI + Uvicorn]
                                    |
                                    v
     Trained Scikit-learn Random Forest Pipeline & ColumnTransformer
                    [StandardScaler + OneHotEncoder]
                                    |
                                    v
                      MySQL 8.0+ Relational Database
        [customers | customer_services | billing_accounts | prediction_history]
```

---

## 🚀 One-Click Quick Start (Windows)

- **Start Everything:** Double-click `start_all.bat` (Starts MySQL, Python ML service, Spring Boot, React, and opens browser to `http://localhost:3000`).
- **Stop Everything:** Double-click `stop_all.bat`.

---

## 🌐 Live URLs

| Service | Technology | Port | URL |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | React + Vite | `3000` | [http://localhost:3000](http://localhost:3000) |
| **Backend REST API** | Java 17 + Spring Boot | `8080` | [http://localhost:8080/api/health](http://localhost:8080/api/health) |
| **ML Inference Service** | Python + FastAPI | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) |
| **Database** | MySQL / MariaDB | `3306` | `127.0.0.1:3306` (Database: `telecom_churn`) |

---

## 📊 Machine Learning Model Telemetry

Trained on the **IBM Telecom Customer Churn Dataset** (7,043 rows) using an 80:20 stratified split (5,634 train / 1,409 held-out test):
- **Model:** Random Forest Classifier (balanced class weights, max_depth=10)
- **Pipeline:** Scikit-learn Pipeline with `ColumnTransformer` (StandardScaler for numerics, OneHotEncoder for categoricals)
- **Test Accuracy:** `75.73%`
- **ROC-AUC Score:** `84.20%`
- **Recall (Sensitivity):** `77.54%`
- **Precision:** `52.92%`
- **F1 Score:** `62.91%`
- **Confusion Matrix:** True Negative: 777 | False Positive: 258 | False Negative: 84 | True Positive: 290

---

## 🗄️ Relational Database Schema (MySQL)

Normalized to Third Normal Form (3NF) under the `telecom_churn` database:
1. `customers`: Demographics (`customer_code`, `gender`, `senior_citizen`, `partner`, `dependents`, `tenure`).
2. `customer_services`: Telecom subscriptions (`phone_service`, `multiple_lines`, `internet_service`, `online_security`, `tech_support`, etc.).
3. `billing_accounts`: Account contract and billing (`contract_type`, `paperless_billing`, `payment_method`, `monthly_charges`, `total_charges`).
4. `prediction_history`: Audited historical ML predictions (`timestamp`, `predicted_class`, `churn_probability`, `risk_level`, `recommendation`, `model_version`, feature snapshot).

All multi-table writes are wrapped in `@Transactional` in `PredictionPersistenceService`.

---

## 🛠️ Manual Startup Instructions

### 1. Database
```bash
# Apply schema
mysql -u root telecom_churn < migrations/01_schema.sql

# Migrate legacy SQLite data to MySQL
python migrations/migrate_data.py
```

### 2. Python ML Service
```bash
# Train model (optional, artifact is pre-saved)
python ml-service/train_model.py

# Run FastAPI
python -m uvicorn app:app --app-dir ml-service --host 127.0.0.1 --port 8000
```

### 3. Java Spring Boot Backend
```bash
# Build
.\mvn.bat -f backend/pom.xml clean package -DskipTests

# Run
java -jar backend/target/churn-prediction-backend-1.0.0.jar
```

### 4. React Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

---

## 🧪 Testing

To run the backend test suite:
```bash
.\mvn.bat -f backend/pom.xml test
```
All unit tests and integration tests pass with 0 errors.
