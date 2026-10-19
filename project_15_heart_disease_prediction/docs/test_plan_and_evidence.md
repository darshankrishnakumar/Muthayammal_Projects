# Quality Assurance Test Plan & Execution Evidence

## Execution Summary
- **Test Framework**: `pytest 9.1.1`
- **Total Tests**: 25
- **Passed**: 25 (100%)
- **Failed**: 0
- **Duration**: 1.85 seconds

## Test Breakdown

### 1. Model & Physiological Tests (`test_model.py` - 8 Tests)
- `test_model_type`: Confirms `RandomForestClassifier` instantiation.
- `test_model_feature_count`: Verifies 11 feature names and counts.
- `test_low_risk_prediction`: Asserts negative prediction on healthy vitals.
- `test_high_risk_prediction`: Asserts positive alert on ischemic patient.
- `test_prediction_output_shapes`: Verifies batch output dimensions and sum-to-one constraints.
- `test_decision_reproducibility`: Validates deterministic predictions across runs.
- `test_risk_tier_calibration`: Confirms 4-tier risk threshold mapping.
- `test_feature_sensitivity_exercise_angina`: Validates that angina significantly elevates risk.

### 2. API Integration Tests (`test_api.py` - 9 Tests)
- `test_health_endpoint`: Asserts status 200, port 5015, and database connection.
- `test_health_alias`: Verifies `/health` alias.
- `test_home_route`: Checks root route serving React SPA.
- `test_api_predict_low_risk`: Validates JSON endpoint on healthy profile.
- `test_api_predict_high_risk`: Validates JSON endpoint on high-risk profile.
- `test_api_predict_invalid_data`: Validates HTTP 400 error response on malformed inputs.
- `test_api_download_report_pdf`: Confirms ReportLab vector PDF compilation (> 1KB binary).
- `test_api_history`: Tests recent patient record pagination.
- `test_api_stats`: Validates aggregate clinical statistics.

### 3. Database Subsystem Tests (`test_database.py` - 5 Tests)
- `test_db_connection`: Verifies SQLite connection and row factory.
- `test_db_init`: Confirms table creation and index integrity.
- `test_log_assessment_and_retrieve`: Verifies transactional INSERT and SELECT.
- `test_database_stats`: Asserts patient counts and average biomarker computations.
- `test_history_limit_slicing`: Tests limit parameter enforcement.

### 4. Audit Verification Tests (`test_audit_verification.py` - 3 Tests)
- `test_docs_exist`: Confirms presence of technical documentation.
- `test_presentation_exists`: Confirms presence of 15-slide presentation.
- `test_requirements_exist`: Confirms presence of dependency file.
