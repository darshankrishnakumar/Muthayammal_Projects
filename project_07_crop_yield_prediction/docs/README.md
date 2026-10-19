# CropAI — Crop Yield Prediction and Decision Support System

**Project Code**: PROJECT-007  
**Academic Domain**: Precision Agriculture / Agronomic Informatics / Applied Machine Learning  
**Core Technologies**: Python 3.12, Flask, Scikit-Learn 1.7+, SQLite3, React 18, Chart.js  
**Operational Port**: `http://127.0.0.1:5007`  

---

## 1. Overview
CropAI is an intelligent precision agriculture decision-support system designed to forecast crop yield density and provide actionable agronomic guidance under shifting climatic conditions.

Trained on multilateral UN FAO and World Bank data spanning 1990 to 2013 across 101 nations and 10 staple crops, CropAI models non-linear interactions between:
- Annual Precipitation (mm/year)
- Average Ambient Temperature (°C)
- Pesticide Application Tonnages
- Geographic Soil Biomes & Chronological Trends

---

## 2. Key Technical Highlights
- **Authentic Global Dataset**: 28,242 verified observations covering 101 sovereign nations and 10 staple crops.
- **115-Feature ColumnTransformer**: Encodes countries and crops with zero-leakage standard scaling.
- **Ensemble Regression Superiority**: Random Forest Regressor achieves **98.5% R²** score.
- **Cultivated Area Calculator**: Computes expected farm harvest in Metric Tonnes and Kilograms across Hectares and Acres.
- **Crop Recommendation Engine**: Simultaneously evaluates and ranks all 10 candidate crops under given climate parameters to advise climate-smart planting alternatives.
- **SQLite Relational Persistence**: Logs valuation queries and historical yields in `cropai_history.db`.
- **28/28 Passing Automated Pytest Tests**: Comprehensive test suite verifying ML pipelines, REST APIs, and database CRUD.

---

## 3. Documentation Suite
- [System Architecture & Dataflow](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/architecture.md)
- [Dataset and Machine Learning Details](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/dataset_and_model_details.md)
- [REST API Documentation](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/api_documentation.md)
- [Setup and Execution Guide](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/setup_and_execution.md)
- [Comprehensive Testing Report](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/testing_report.md)
- [Limitations and Future Work](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/limitations_and_future_work.md)
- [Third-Party Notices](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/third_party_notices.md)
- [Final Project Acceptance Report](file:///Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/acceptance_report.md)
