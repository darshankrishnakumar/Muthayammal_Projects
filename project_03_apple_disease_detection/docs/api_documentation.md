# API Specification (OpenAPI 3.0 Standard)

Base URL: `http://localhost:5003`

---

### 1. Health & System Readiness Probe
- **Endpoint**: `GET /health`
- **Description**: Verifies service status, active deep learning models, loaded checkpoint classes, and SQLite database connectivity.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "system": "Apple Health Intelligence AI (Multi-Task Pomological & Foliar Diagnostic Suite)",
  "port": 5003,
  "models": {
    "fruit_condition": {
      "active": true,
      "classes": ["Fresh", "Rotten"]
    },
    "leaf_disease": {
      "active": true,
      "classes": ["Apple_Scab", "Black_Rot", "Cedar_Apple_Rust", "Healthy"]
    },
    "input_validator": {
      "active": true,
      "classes": ["apple_fruit", "apple_leaf", "unsupported"]
    },
    "legacy_custom_cnn": {
      "active": true,
      "classes": ["Apple_Scab", "Black_Rot", "Cedar_Apple_Rust", "Healthy_Apple", "Apple_Blotch"]
    }
  },
  "database": {
    "connected": true,
    "total_records": 28,
    "specimen_breakdown": {
      "apple_fruit": 18,
      "apple_leaf": 10
    }
  }
}
```

---

### 2. Validated Preset Sample Gallery
- **Endpoint**: `GET /api/samples`
- **Description**: Returns authenticated test specimens across leaf and fruit conditions with base64 thumbnail previews.
- **Response `200 OK`**:
```json
{
  "success": true,
  "samples": {
    "cedar_rust": {
      "title": "Cedar Apple Rust (Leaf)",
      "pathogen": "Gymnosporangium juniperi-virginianae",
      "thumbnail": "data:image/jpeg;base64,..."
    },
    "scab_leaf": { ... },
    "black_rot_leaf": { ... },
    "healthy_leaf": { ... },
    "scab_fruit": { ... },
    "rot_fruit": { ... },
    "blotch_fruit": { ... }
  }
}
```

---

### 3. Leaf & Fruit Disease Diagnosis
- **Endpoint**: `POST /api/predict`
- **Description**: Accepts either multipart image upload or JSON payload with base64/sample_id. Executes multi-task inference and returns diagnosis, confidence, Grad-CAM heatmap, and remedies.
- **Request (Multipart Form-Data)**:
  - `image`: binary image file
  - `model_type`: `"transfer"` or `"custom"`
  - `specimen`: `"auto"`, `"leaf"`, or `"fruit"`
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "predicted_class": "Cedar_Apple_Rust",
    "display_name": "Cedar Apple Rust",
    "latin_name": "Gymnosporangium juniperi-virginianae",
    "specimen_type": "apple_leaf",
    "confidence": 99.4,
    "severity": "High Severity",
    "severity_level": 4,
    "is_uncertain": false,
    "gradcam_image": "data:image/jpeg;base64,...",
    "decision_support": {
      "pesticide_suggestions": [
        {
          "name": "Myclobutanil (Rally 40WSP)",
          "type": "DMI / FRAC Group 3",
          "rate": "5.0 oz / acre",
          "timing": "Pink bud through petal fall"
        }
      ],
      "organic_remedies": [
        {
          "name": "Liquid Lime Sulfur",
          "usage": "2 gal / 100 gal water at delayed dormant"
        }
      ],
      "preventive_measures": [
        "Eradicate eastern red cedar trees within a 1-mile radius where feasible"
      ]
    },
    "db_record_id": 29
  }
}
```

---

### 4. Database Audit Stream
- **Endpoint**: `GET /api/db/history?limit=10`
- **Description**: Retrieves transactional diagnosis records from SQLite store.
- **Response `200 OK`**:
```json
{
  "success": true,
  "records": [
    {
      "id": 29,
      "timestamp": "2026-10-18T17:42:15Z",
      "specimen_type": "apple_leaf",
      "predicted_class": "Cedar_Apple_Rust",
      "display_name": "Cedar Apple Rust",
      "confidence": 99.4,
      "model_used": "MobileNetV2",
      "severity": "High Severity"
    }
  ]
}
```

---

### 5. Agronomic Pathology Encyclopedia
- **Endpoint**: `GET /api/encyclopedia`
- **Description**: Returns detailed pathology guides, symptomology, and chemical/organic prescriptions for all 5 conditions.
