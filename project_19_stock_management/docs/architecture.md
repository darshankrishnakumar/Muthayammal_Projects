# Enterprise Architecture & System Topology

## 1. System Overview
Project-019 delivers **Stock Management System Pro (SMS)**, an enterprise-grade cyber-physical inventory management platform uniting Internet of Things (IoT) hardware telemetry, operations research mathematical modeling, and deep recurrent time-series demand forecasting.

```
+-------------------------------------------------------------------------------+
|                             PRESENTATION TIER                                 |
|   HTML5 / CSS3 Dark Glassmorphism SPA • Canvas Sales Velocity • Port 5019      |
+---------------------------------------+---------------------------------------+
                                        | HTTP REST (JSON)
+---------------------------------------v---------------------------------------+
|                             APPLICATION TIER                                  |
|   Python Flask 3.1 • CORS Middleware • Transactional Session Controller       |
|   Hardware Event Dispatcher • Dynamic ROP / EOQ Optimizer                     |
+---------------------------------------+---------------------------------------+
                    |                                       |
+-------------------v-------------------+       +-----------v-------------------+
|            NEURAL & ML TIER           |       |        DATA & IOT TIER        |
|  • PyTorch Bi-LSTM (43K Params)       |       |  • Relational SQLite / MySQL  |
|  • Scikit-Learn Random Forest         |       |  • Optical 1D/2D Barcode      |
|  • Gradient Boosting Regressor        |       |  • UHF RFID Portal Gate       |
|  • ARIMA(2,1,2) Baseline              |       |  • RS232 Smart Weighing Scale |
+---------------------------------------+       +-------------------------------+
```

## 2. Component Specifications
- **Presentation Layer**: Responsive dark glassmorphism dashboard featuring six operational tabs: Inventory & POS Sales, Barcode & RFID Scanner, Wholesaler Orders & Shipments, 7-Day AI Demand Forecast, Reports & CSV Export, and Neural Architecture & ML Forensics.
- **Application Engine**: Python 3.12 with Flask 3.1, providing RESTful endpoints, CORS headers, hardware simulation logic, and transactional database commit handling.
- **AI Forecasting Engine**: PyTorch Bi-Directional LSTM (2 layers, 64 hidden units, dropout 0.20) ensembled with 100-tree Random Forest and 100-stage Gradient Boosting regressors.
- **Data Persistence**: SQLAlchemy 2.0 dual-mode driver supporting cloud MySQL with automatic zero-configuration local SQLite fallback (`stock_management.db`).
