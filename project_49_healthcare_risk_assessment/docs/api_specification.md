# API Specification — PROJECT-049
## Port 5049 Microservice Endpoints

### 1. Health & System Diagnostics
- **`GET /api/health/`**
  - **Description**: Returns microservice status, active port, SQLite WAL configuration, and loaded model parameters.
  - **Response (200 OK)**:
    ```json
    {
      "status": "HEALTHY",
      "service": "Project 49 Healthcare Risk Assessment API",
      "project_id": "PROJECT-049",
      "port": 5049,
      "database_wal_mode": true,
      "cuda_available": false,
      "mps_available": true,
      "models": {
        "risk_model": "LongitudinalHealthRiskNet",
        "risk_parameters": 3044,
        "comorbidity_model": "ClinicalComorbidityForecastNet",
        "comorbidity_parameters": 18308
      }
    }
    ```

### 2. Clinical Risk Assessment
- **`POST /api/patients/assess`** (Aliased: `POST /api/patients/evaluate`)
  - **Description**: Evaluates 10 physiological biomarkers via dual PyTorch neural engines, computing disease risks, comorbidity forecasts, and SHAP attributions.
  - **Request Body**:
    ```json
    {
      "full_name": "Robert Vance",
      "patient_id": "PAT-901",
      "age": 58,
      "gender": "Male",
      "systolic_bp": 148.0,
      "diastolic_bp": 92.0,
      "hba1c": 7.2,
      "fasting_glucose": 145.0,
      "cholesterol": 230.0,
      "hdl": 42.0,
      "ldl": 158.0,
      "egfr": 58.0,
      "bmi": 31.4
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "assessment": { ... },
      "metrics": {
        "cardiovascular_risk_pct": 74.2,
        "type2_diabetes_risk_pct": 68.5,
        "hypertension_risk_pct": 82.0,
        "ckd_risk_pct": 34.0,
        "composite_risk_tier": "HIGH",
        "ten_year_mortality_risk_pct": 42.5,
        "hospital_readmission_risk_pct": 38.0,
        "top_shap_driver": "Systolic Blood Pressure (+0.38)",
        "evidence_hash": "..."
      }
    }
    ```

### 3. Patient & Audit Endpoints
- **`GET /api/patients/assessments`** (Aliased: `GET /api/patients/records` and `GET /api/health-risk/records`): Returns clinical assessments.
- **`GET /api/patients/profiles`**: Returns registered patient profiles.
- **`GET /api/patients/audit-logs`**: Returns cryptographic audit blocks with chain verification.
- **`GET /api/patients/stats`**: Provides cohort counts and risk tier breakdowns.
- **`GET /api/analytics/summary`**: High-level platform statistics for dashboard KPI cards.
