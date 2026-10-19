# Demonstration & Walkthrough Script: CAR PRICE PREDICTION (PROJECT-004)

## Overview
- **Project Identifier**: PROJECT-004
- **Official Title**: CAR PRICE PREDICTION
- **Module**: `project_04_car_price_prediction`
- **Recorded Duration**: 03:00 (180.0 Seconds)
- **Target Video**: `walkthrough/walkthrough_video.mp4`

---

## Detailed Chronological Demonstration Script

### 1. 00:00 - 00:30 | Phase 1: Platform Overview & System Health
- **Visual**: Browser opens `http://127.0.0.1:5004` displaying the AutoValuate AI automotive intelligence dashboard.
- **Key Points**:
  - Live system heartbeat indicator confirms FastAPI microservice is online on Port 5004.
  - Top KPI cards highlight optimal production model (Random Forest Regressor, 150 trees), test $R^2$ accuracy (97.23%), low mean absolute error (₹0.88 Lakhs / ~$1,060 USD), and 450 verified training sales records.

### 2. 00:30 - 01:05 | Phase 2: Commuter & Executive Vehicle Valuations
- **Visual**: Click on quick preset #1: Maruti Suzuki Swift VXI (2018).
- **Key Points**:
  - Automatically populates vehicle configuration form: ₹7.2L showroom price, 45,000 km, petrol manual.
  - Valuation inference executes in sub-8ms, estimating market fair value at ₹4.25 Lakhs (~$5,100 USD) with "Good Value Retention" and 40.9% depreciation.
  - Inspect 90% confidence bounds (₹3.80L – ₹4.70L) and 10-year value decay curve.
  - Click on preset #2: Honda City ZX (2020), demonstrating executive sedan valuation (₹9.42 Lakhs).

### 3. 01:05 - 01:40 | Phase 3: Premium SUV & German Luxury Demonstrations
- **Visual**: Click on preset #4: Toyota Fortuner 4x4 (2021) and preset #5: BMW 3 Series 330i (2021).
- **Key Points**:
  - Toyota Fortuner (₹42.0L showroom, diesel AT) demonstrates exceptional Japanese utility equity preservation.
  - BMW 3 Series (₹54.0L showroom) highlights rapid non-linear luxury depreciation curves.

### 4. 01:40 - 02:15 | Phase 4: Model Benchmarks & Feature Importance Hierarchy
- **Visual**: Switch to "Model Benchmarks" and "Feature Importance" tabs.
- **Key Points**:
  - Comparative benchmark cards display side-by-side performance of Random Forest ($R^2=0.9723$), Decision Tree ($R^2=0.9525$), and Linear Regression ($R^2=0.8968$).
  - Feature importance ranking visualizers confirm Showroom Price (75.14%), Vehicle Age (13.30%), and Odometer Mileage (9.31%) account for over 97% of valuation variance.

### 5. 02:15 - 02:45 | Phase 5: Transactional Audit Log & Dataset Explorer
- **Visual**: Switch to "Prediction History" and "Dataset Explorer" tabs.
- **Key Points**:
  - Transactional SQLite table (`predictions.db`) displays live audit logs for each evaluated vehicle with brand, model, price, retention badge, and individual deletion capability.
  - Dataset explorer samples historical sales transactions from `car_data.csv`.

### 6. 02:45 - 03:00 | Phase 6: Conclusion & Engineering Verification
- **Visual**: Switch to "REST API Docs" tab and display system verification summary.
- **Key Points**:
  - OpenAPI endpoint specifications confirmed.
  - 18/18 automated pytest test cases verified passing with 100% pass rate.
  - Full project sign-off confirmed for final college submission.
