# RESTful API Specification: ROAD-AI (Port 5034)

## Base URL
`http://127.0.0.1:5034/api`

## Endpoints

### 1. GET `/health`
Returns microservice operational status, model weights verification, and monitored sector count.
**Response (200 OK):**
```json
{
  "classes_supported": 5,
  "classifier_accuracy": "76.08%",
  "model": "YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)",
  "model_framework": "PyTorch 2.x Deep Residual Feature Extractor & Dual-Head Regressor",
  "monitored_sectors": 5,
  "port": 5034,
  "service": "AI Road Damage Detection & Severity Classifier API",
  "status": "healthy"
}
```

### 2. POST `/detect`
Executes forward tensor evaluation through both PyTorch models.
**Request Body:**
```json
{
  "sector_id": "SEC-NORTH-01",
  "damage_type": "POTHOLE",
  "scenario": "auto"
}
```
*Note: Accepts either `sector_id` or `sector`, and optional `damage_type` (`POTHOLE`, `ALLIGATOR`, `CRACK`, `RUTTING`, `D40`, etc.).*

**Response (200 OK):**
```json
{
  "defects": [
    {
      "area_sqm": 1.44,
      "bbox": { "h": 0.2, "w": 0.28, "x": 0.22, "y": 0.42 },
      "code": "D40",
      "color": "#ef4444",
      "confidence": 0.942,
      "confidence_pct": 94.2,
      "defect_name": "D40 - Deep Pothole",
      "estimated_cost_usd": 201,
      "recommended_action": "Cold/hot asphalt pothole patch & compactor roll",
      "severity": "HIGH"
    }
  ],
  "defects_found_count": 2,
  "iri_roughness_m_km": 3.42,
  "model": "YOLOv8x Deep Road Damage Detector (RDD2022 Benchmark)",
  "pci_rating": "FAIR (MAINTENANCE REQUIRED)",
  "pci_score": 62.4,
  "sector_id": "SEC-NORTH-01",
  "sector_name": "Highway Sector A4 (Expressway Corridor)",
  "status_color": "#f59e0b",
  "total_area_sqm": 2.4,
  "total_repair_cost_usd": 296
}
```

### 3. GET `/sectors`
Returns metadata and speed limits for all 5 registered roadway sectors.

### 4. GET `/defects/catalog`
Returns the standardized RDD2022 defect taxonomy with repair costs.

### 5. GET `/stats`
Returns aggregated municipal survey statistics: total surveys, total defects, repair budget, mean PCI, and YOLO mAP@50.

### 6. GET & POST `/work-orders`
Retrieves and creates Municipal Work Orders (MWO) for pavement contractor dispatch.

### 7. GET `/audit-logs`
Returns the immutable DOT/municipal regulatory audit trail.

### 8. GET `/model/info`
Returns PyTorch deep learning parameters and RDD2022 training convergence metrics.
