# REST API Documentation - CropAI

The CropAI microservice runs on `http://127.0.0.1:5007`.

---

## 1. System Metadata & Stats

### `GET /api/stats`
Returns total dataset statistics, country count, crop count, and historical range.

**Response (200 OK):**
```json
{
  "countries": 101,
  "crops": 10,
  "records": 28242,
  "trainMean": 76740.18,
  "yearMax": 2013,
  "yearMin": 1990
}
```

### `GET /api/options`
Returns sorted arrays of supported nations and staple crops.

---

## 2. Model Performance Endpoints

### `GET /api/models/regression`
Returns comparative evaluation metrics ($R^2$, RMSE, MAE) across all trained regression models.

### `GET /api/classification?type=binary|3class`
Returns accuracy, precision, recall, and confusion matrix for classification tasks.

---

## 3. Crop Yield Prediction

### `POST /api/predict`
Calculates predicted yield density (hg/ha), harvest output in metric tonnes / kg, and logs the query to SQLite.

**Request Payload:**
```json
{
  "country": "Albania",
  "crop": "Maize",
  "year": 2010,
  "rain": 1485.0,
  "pest": 121.0,
  "temp": 16.4,
  "model": "Random Forest",
  "farm_area": 5.0,
  "farm_area_unit": "ha"
}
```

**Response (200 OK):**
```json
{
  "predicted_yield_hg_ha": 52480.5,
  "predicted_yield_tonnes_ha": 5.248,
  "confidence_interval_95": [49800.0, 55160.0],
  "model_used": "Random Forest",
  "unit": "hg/ha",
  "farm_area": 5.0,
  "farm_area_unit": "ha",
  "farm_area_ha": 5.0,
  "total_production_tonnes": 26.24,
  "total_production_kg": 26240.25,
  "history_id": 42
}
```

---

## 4. Crop Recommendation Engine

### `POST /api/recommend`
Evaluates all 10 staple crops under specified environmental conditions and returns the top-ranked options.

**Request Payload:**
```json
{
  "country": "India",
  "year": 2013,
  "rain": 1200.0,
  "pest": 50000.0,
  "temp": 26.5
}
```

**Response (200 OK):**
```json
{
  "country": "India",
  "recommendations": [
    { "crop": "Potatoes", "predicted_yield_hg_ha": 215400.0, "rank": 1 },
    { "crop": "Cassava", "predicted_yield_hg_ha": 182300.0, "rank": 2 },
    { "crop": "Sweet Potatoes", "predicted_yield_hg_ha": 145000.0, "rank": 3 }
  ]
}
```

---

## 5. History & Audit Trail

### `GET /api/history?limit=25`
Retrieves past valuation queries stored in `cropai_history.db`.
