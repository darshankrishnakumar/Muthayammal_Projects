# System Architecture & Technical Design

## Architectural Overview

AutoValuate AI is structured as a decoupled multi-layer system separating model training, preprocessing pipelines, transactional persistence, REST microservices, and interactive web presentation.

```mermaid
flowchart TD
    subgraph Client Layer
        Browser["Responsive Web Dashboard<br/>(HTML5 / CSS3 / Vanilla JS)"]
        PresetSelector["Quick Preset Selector<br/>(5 Curated Vehicles)"]
    end

    subgraph Service Layer - FastAPI :5004
        APIGateway["FastAPI Gateway<br/>(CORS / Routing)"]
        PredictEndpoint["POST /api/predict"]
        HistoryEndpoint["GET/DELETE /api/history"]
        AnalyticsEndpoint["GET /api/analytics"]
        PresetsEndpoint["GET /api/presets"]
    end

    subgraph ML Pipeline Layer - Scikit-Learn
        PydanticValidator["Pydantic Input Validator<br/>(CarInputSchema)"]
        Preprocessor["ColumnTransformer<br/>• StandardScaler (Continuous)<br/>• OneHotEncoder (Categorical)"]
        ModelCache["Model Cache<br/>• Random Forest (150 trees)<br/>• Decision Tree (depth 7)<br/>• Linear Regression (OLS)"]
        ConfidenceEstimator["90% Confidence Interval Estimator<br/>(z = 1.645 * Scaled RMSE)"]
    end

    subgraph Persistence Layer
        SQLiteDB[("SQLite Store<br/>predictions.db")]
        HistoricalCSV[("Kaggle Benchmark<br/>car_data.csv (450 rows)")]
        ModelArtifacts[("Joblib Artifacts<br/>best_car_price_model.joblib")]
    end

    Browser -->|HTTP Requests| APIGateway
    PresetSelector --> Browser
    APIGateway --> PredictEndpoint
    APIGateway --> HistoryEndpoint
    APIGateway --> AnalyticsEndpoint
    APIGateway --> PresetsEndpoint

    PredictEndpoint --> PydanticValidator
    PydanticValidator --> Preprocessor
    Preprocessor --> ModelCache
    ModelCache --> ConfidenceEstimator
    ConfidenceEstimator --> SQLiteDB
    HistoryEndpoint --> SQLiteDB
    AnalyticsEndpoint --> SQLiteDB
    ModelCache -.-> ModelArtifacts
    APIGateway -.-> HistoricalCSV
```

## Layer Specifications

### 1. Client Presentation Layer
- Built with standard HTML5, modern CSS3 variables, and Vanilla JavaScript with zero external CDN dependencies.
- Features six dedicated tabs: Valuation Engine, Model Benchmarks, Feature Importance, Prediction History, Dataset Explorer, and REST API Documentation.
- Renders dynamic 10-year value depreciation bars using pure CSS calculations.

### 2. FastAPI Microservice Gateway (Port 5004)
- High-concurrency asynchronous ASGI server running via Uvicorn.
- Strict Pydantic input schema validation preventing invalid vehicle parameters (negative prices, future manufacturing years, exorbitant mileage).

### 3. Machine Learning Regression Pipeline
- Encapsulated within `sklearn.pipeline.Pipeline`.
- Transforms raw multi-modal tabular data (continuous numbers and categorical strings) into a 22-dimensional feature tensor.
- Returns fair market valuations, confidence bounds, depreciation percentages, and value retention ratings.

### 4. Database Layer
- SQLite database (`source_code/data/predictions.db`) maintaining the `prediction_history` table for historical auditability and analytics.
