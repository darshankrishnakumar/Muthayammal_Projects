# System Architecture & Technical Design

## High-Level Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Client Layer (Browser)                         │
│  - Vanilla HTML5 / Modern CSS Glassmorphism UI                         │
│  - Tabbed Workflow: Valuation Engine, Performance, History, Analytics │
│  - Real-Time Async REST Client (Fetch API)                            │
└─────────────────────────────────▲──────────────────────────────────────┘
                                  │ HTTP / JSON (Port 5001)
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Application Gateway (FastAPI Layer)                  │
│  - CORS Middleware & Static File Mounting                              │
│  - Pydantic v2 Request Validation & Schema Serialization               │
│  - Endpoints: /api/predict, /api/options, /api/metrics, /api/history    │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│        Machine Learning Subsystem    │ │        Database Subsystem     │
│  - Preprocessor (ColumnTransformer)  │ │  - SQLite3 Engine (airfare.db)│
│    • StandardScaler (Cont. Features) │ │  - Schema: prediction_logs    │
│    • OneHotEncoder (Categoricals)    │ │  - Async Logging of Requests  │
│  - Dual Inference Engine:            │ │  - Analytical Aggregations    │
│    • PyTorch 2.0 BiLSTM Regressor    │ │    (Daily stats, route avgs)  │
│    • Random Forest Regressor (100 T) │ └───────────────────────────────┘
│  - Dynamic Rule Adjustments          │
│    (Stop count penalties, bounds)    │
└──────────────────────────────────────┘
```

## Data Flow & Processing Pipeline

1. **User Input Ingestion**: The user specifies airline carrier, origin/destination city pair, departure date/time, arrival time, total stopovers, and optional amenities.
2. **Schema Validation**: FastAPI validates input using `FlightPredictionRequest` Pydantic model:
   - Date formats (`YYYY-MM-DD`, `HH:MM`).
   - Allowable airline categories and route geography.
   - Non-negative integer constraints for stops.
3. **Temporal Feature Extraction**:
   - $\text{Duration (min)} = (\text{Arrival Date/Time} - \text{Departure Date/Time})$.
   - Extraction of `journey_day`, `journey_month`, `dep_hour`, `dep_min`, `arr_hour`, `arr_min`.
4. **Feature Encoding & Scaling**:
   - Continuous inputs transformed via fitted `StandardScaler`.
   - Categorical inputs encoded into 24-dimensional one-hot vectors via `OneHotEncoder`.
   - Total transformed feature vector: $\mathbf{x} \in \mathbb{R}^{31}$.
5. **Model Inference**:
   - BiLSTM: Vector $\mathbf{x}$ unsqueezed to shape $(1, 1, 31)$, propagated through 2-layer Bidirectional LSTM ($\text{hidden\_size}=64$, $\text{dropout}=0.2$), pooled, and passed through linear head ($\mathbb{R}^{128} \to \mathbb{R}^{64} \to \mathbb{R}^1$).
   - Random Forest: 100 decision trees averaged.
   - Stop penalties applied: ₹1,500/stop for direct/multi-stop discrepancy corrections.
   - 95% Confidence bounds computed based on empirical standard error $\pm 1.96 \cdot \sigma_\epsilon$.
6. **Persistence**:
   - Prediction payload, timestamps, inputs, and inference latency logged transactionally to `source_code/data/airfare.db`.
7. **Client Rendering**:
   - Result rendered with interactive fare breakdown, confidence interval gauge, and dynamic multi-currency conversions (INR, USD, EUR, GBP).
