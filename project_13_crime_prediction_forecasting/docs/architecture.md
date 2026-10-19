# System Architecture & Technical Design

## 1. High-Level Architecture

PROJECT-013 is an enterprise spatio-temporal crime prediction and tactical dispatching platform built with FastAPI, PyTorch, Scikit-Learn, and SQLite.

```
+-----------------------------------------------------------------------------------+
|                        URBAN CRIME COMMAND DASHBOARD                              |
|           Tailwind CSS, FontAwesome, Dynamic Hourly Temporal Curve Chart          |
+-----------------------------------------------------------------------------------+
                                        |  HTTP/REST (Port 5013)
                                        v
+-----------------------------------------------------------------------------------+
|                         FASTAPI MICROSERVICE (main.py)                            |
|  /health | /api/districts | /api/predict_risk | /api/forecast_hourly | /api/dispatch  |
+-----------------------------------------------------------------------------------+
                   |                                             |
                   v                                             v
+---------------------------------------+       +-----------------------------------+
|       AI/ML INFERENCE ENGINE          |       |      DATABASE SUBSYSTEM           |
|                                       |       |       (crime_incident.db)         |
|  - StandardScaler Normalizer          |       |  - 'crime_incidents' Table        |
|  - PyTorch CrimeRiskDNN (11-128-64-4) |       |  - 'patrol_dispatches' Table      |
|  - Random Forest Classifier (150-tree)|       |  - B-Tree Indexes on Timestamp    |
|  - 24-Hour Hourly Risk Generator      |       |  - ACID Transactional Persistence |
+---------------------------------------+       +-----------------------------------+
```

## 2. Component Specifications

### 2.1 Backend Server (source_code/backend/main.py)
High-performance ASGI microservice running on Port 5013. Exposes 10 validated endpoints with Pydantic type checking and structured error responses.

### 2.2 Deep Learning Forecaster (CrimeRiskDNN)
PyTorch deep neural network mapping 11 spatio-temporal features to 4 calibrated threat tiers:
- CRITICAL (Severe felony offenses, Code 3 dispatch)
- HIGH (Elevated property/battery risk, sector alert)
- MODERATE (Routine disturbances)
- LOW (Baseline urban state)

### 2.3 Crime Type Classifier
Random Forest classifier (150 trees) predicting fine-grained offense types: THEFT, BATTERY, BURGLARY, ROBBERY, NARCOTICS, ASSAULT, VANDALISM, and WEAPONS VIOLATION.

### 2.4 Command Ledger Database (source_code/data/crime_incident.db)
SQLite relational database maintaining complete audit logs of all historical incident predictions and active squad car fleet dispatches.
