# Testing and Verification Report

**Project**: `PROJECT-004: Car Price Prediction & Automotive Valuation Engine`  
**Test Suite**: `source_code/tests/test_api_and_model.py`  
**Test Framework**: Pytest 9.1.1 (Python 3.12.8)  
**Execution Time**: 2.51s  
**Results**: 18 Passed, 0 Failed (100% Pass Rate)

---

## Detailed Test Case Registry

| Test ID | Test Function Name | Subsystem Verified | Pass / Fail | Description |
|---|---|---|---|---|
| TC-01 | `test_model_loading_artifacts` | Model Serialization | **PASS** | Confirms `.joblib` and `.pkl` model artifacts load and contain `predict` method. |
| TC-02 | `test_random_forest_is_trained` | Regressor Structure | **PASS** | Verifies Random Forest contains 150 fitted estimators and non-trivial trees. |
| TC-03 | `test_evaluation_metrics_and_reproducibility` | Evaluation Metrics | **PASS** | Validates held-out test split produces $R^2 \ge 0.95$ and low MAE. |
| TC-04 | `test_health_check_endpoint` | API Gateway | **PASS** | Verifies `GET /api/health` returns healthy status and lists models. |
| TC-05 | `test_model_metadata_endpoint` | Metadata API | **PASS** | Verifies feature importances sum to ~100% and metadata fields are intact. |
| TC-06 | `test_predict_endpoint_all_algorithms` | Inference Engine | **PASS** | Runs prediction across Random Forest, Decision Tree, and Linear Regression. |
| TC-07 | `test_predict_input_validation_boundary_conditions` | Pydantic Schema | **PASS** | Verifies 12 boundary error conditions return HTTP 422 Unprocessable Entity. |
| TC-08 | `test_sqlite_database_crud_persistence` | Database CRUD | **PASS** | Validates SQLite prediction insertion, retrieval, and single record deletion. |
| TC-09 | `test_dataset_sample_endpoint` | Dataset API | **PASS** | Verifies `GET /api/dataset/sample` returns 5 sample records from CSV. |
| TC-10 | `test_presets_endpoint` | Presets API | **PASS** | Validates `GET /api/presets` returns $\ge 4$ preset vehicle specifications. |
| TC-11 | `test_analytics_endpoint` | Market Analytics | **PASS** | Confirms `GET /api/analytics` computes total predictions, average prices, and retention tiers. |
| TC-12 | `test_root_index_html` | Web Presentation | **PASS** | Confirms `GET /` serves HTML containing AutoValuate AI portal elements. |
| TC-13 | `test_prediction_with_each_preset` | Multi-Segment Valuations | **PASS** | Confirms inference succeeds for all preset vehicle payloads within bounds. |
| TC-14 | `test_feature_importance_consistency` | Interpretability | **PASS** | Confirms top 3 features are Present_Price, Car_Age, and Kms_Driven. |
| TC-15 | `test_decision_tree_estimator_depth` | CART Regressor | **PASS** | Confirms decision tree depth $\le 8$ and 22 one-hot features in input space. |
| TC-16 | `test_linear_regression_coefficients` | Linear Baseline | **PASS** | Verifies linear regression has valid coefficients and fitted intercept. |
| TC-17 | `test_extreme_mileage_and_age_depreciation` | Valuation Bounds | **PASS** | Confirms older cars with high mileage experience $\ge 50\%$ depreciation. |
| TC-18 | `test_clear_and_repopulate_history` | History Reset | **PASS** | Validates `DELETE /api/history` wipes records and resets table to empty. |
