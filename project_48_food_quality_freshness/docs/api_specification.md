# API Specification — PROJECT-048
## Port 5048 Microservice Endpoints

### 1. Health & System Diagnostics
- **`GET /api/health/`**
  - **Description**: Returns microservice status, active port, SQLite WAL configuration, and loaded model parameters.
  - **Response (200 OK)**:
    ```json
    {
      "status": "HEALTHY",
      "service": "Project 48 Food Quality & Freshness Detection API",
      "project_id": "PROJECT-048",
      "port": 5048,
      "database_wal_mode": true,
      "cuda_available": false,
      "mps_available": true,
      "models": {
        "cnn_model": "SpectralFreshnessCNN",
        "cnn_parameters": 20869,
        "regressor_model": "ShelfLifeForecastRegressorNet",
        "regressor_parameters": 18052
      }
    }
    ```

### 2. Quality Evaluation
- **`POST /api/freshness/evaluate`** (Aliased: `POST /api/food/inspect`)
  - **Description**: Evaluates spatio-spectral image patch and 10 physicochemical inputs via dual PyTorch models.
  - **Request Body**:
    ```json
    {
      "product_name": "Prime Ribeye Beef Cut",
      "food_category": "MEAT_POULTRY",
      "simulate_spoilage": false,
      "storage_temp_c": 2.8,
      "relative_humidity_pct": 84.0,
      "browning_index": 1.1,
      "tvbn_mg_per_100g": 7.5
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "sample_id": "FOOD-B2A8C1",
      "food_name": "Prime Ribeye Beef Cut",
      "freshness_score": 91.8,
      "safety_status": "FRESH",
      "remaining_shelf_life_days": 6.8,
      "advisory_note": "OPTIMAL RETAIL SALE: 6.8 days remaining at 2.8°C",
      "batch": { ... },
      "metrics": { ... }
    }
    ```

### 3. Inventory & Audit Endpoints
- **`GET /api/freshness/batches`** (Aliased: `GET /api/food/records`): Returns registered perishable batches.
- **`GET /api/freshness/assessments`**: Returns full historical inspection records with evidence hashes.
- **`GET /api/freshness/audit-logs`**: Returns cryptographic blocks with on-the-fly hash chain continuity verification.
- **`GET /api/freshness/stats`**: Summarizes batch counts, stage distribution, and mean quality indices.
- **`GET /api/analytics/summary`**: High-level platform statistics for dashboard KPI cards.
