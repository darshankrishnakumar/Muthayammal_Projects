# REST API Documentation

The AutoValuate AI microservice provides asynchronous REST endpoints running on `http://localhost:5004`.

---

## 1. Health & Status

### `GET /api/health`
Returns system heartbeat and in-memory model availability.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "models_loaded": [
    "best",
    "Random Forest Regression",
    "Decision Tree Regression",
    "Linear Regression"
  ],
  "has_metadata": true
}
```

---

## 2. Presets Catalog

### `GET /api/presets`
Returns curated vehicles for instant interactive testing.

**Response (200 OK):**
```json
[
  {
    "id": "swift-2018",
    "name": "Maruti Suzuki Swift VXI",
    "category": "Commuter Hatchback",
    "brand": "Maruti",
    "car_model": "Swift",
    "year": 2018,
    "present_price": 7.2,
    "kms_driven": 45000.0,
    "fuel_type": "Petrol",
    "seller_type": "Dealer",
    "transmission": "Manual",
    "owner": 0,
    "algorithm": "Random Forest Regression"
  }
]
```

---

## 3. Valuation Prediction

### `POST /api/predict`
Executes regression pipeline and returns price prediction, 90% confidence bounds, and depreciation analysis.

**Request Body (`application/json`):**
```json
{
  "brand": "Honda",
  "car_model": "City",
  "year": 2020,
  "present_price": 14.5,
  "kms_driven": 32000.0,
  "fuel_type": "Petrol",
  "seller_type": "Dealer",
  "transmission": "Automatic",
  "owner": 0,
  "algorithm": "Random Forest Regression"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "history_id": 4,
  "predicted_price_lakhs": 9.42,
  "predicted_price_usd": 11304,
  "original_price_lakhs": 14.5,
  "original_price_usd": 17400,
  "depreciation_percentage": 35.0,
  "depreciation_amount_lakhs": 5.08,
  "retention_rating": "Good",
  "confidence_range": {
    "lower_lakhs": 8.39,
    "upper_lakhs": 10.45,
    "lower_usd": 10068,
    "upper_usd": 12540
  },
  "model_details": {
    "algorithm": "Random Forest Regression",
    "r2_score": 0.9723,
    "rmse": 1.3989,
    "mae": 0.8835
  },
  "vehicle_summary": {
    "brand": "Honda",
    "car_model": "City",
    "year": 2020,
    "age_years": 4,
    "mileage_kms": 32000,
    "fuel_type": "Petrol",
    "transmission": "Automatic",
    "seller_type": "Dealer",
    "previous_owners": 0
  }
}
```

---

## 4. History & Analytics

### `GET /api/history`
Returns historical predictions stored in SQLite. Optional query parameter: `?limit=50`.

### `DELETE /api/history/{record_id}`
Deletes a specific prediction entry by ID.

### `DELETE /api/history`
Clears the entire prediction history table.

### `GET /api/analytics`
Returns aggregate market valuation statistics, average depreciation rate, and brand distributions.
