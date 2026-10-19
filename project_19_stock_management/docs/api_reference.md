# REST API Reference & Data Contracts

All endpoints are hosted on `http://127.0.0.1:5019/api` and accept/return JSON payloads.

### 1. System Health
- **Endpoint**: `GET /api/health`
- **Response**:
```json
{
  "database": "SQLite",
  "service": "Enterprise Stock Management System (SMS) API",
  "status": "running",
  "version": "2.0-Enterprise"
}
```

### 2. Dashboard Metrics
- **Endpoint**: `GET /api/dashboard`
- **Response**: Summary of total products, valuations, margins, low stock alerts, and 7-day sales velocity.

### 3. Product Catalog
- **Endpoint**: `GET /api/products?search=&category_id=`
- **Response**: Array of product objects including SKU, price, cost price, live quantity, ROP, barcode, and RFID tags.

### 4. Demand Forecast
- **Endpoint**: `GET /api/forecast?sku=SKU-001`
- **Response**: 7-day forecast series, actuals, predicted values, confidence bounds, dynamic ROP alerts, and model evaluation metrics.

### 5. Hardware Scan
- **Endpoint**: `POST /api/hardware/scan`
- **Payload**: `{"code": "8901001001", "action": "LOOKUP | SALE | INWARD", "device_id": "SCANNER-W01"}`

### 6. Smart Scale Telemetry
- **Endpoint**: `POST /api/hardware/telemetry`
- **Payload**: `{"sku": "SKU-001", "weight_kg": 11.25, "unit_weight_kg": 0.25}`
- **Response**: Measured vs calculated counts, discrepancy, and status (`MATCH | DEFICIT | SURPLUS`).

### 7. CSV Export
- **Endpoint**: `GET /api/reports/export?type=products | sales | movements`
- **Response**: Formatted CSV data stream.
