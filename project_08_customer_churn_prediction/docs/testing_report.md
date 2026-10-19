# Automated Testing Report: Customer Churn Intelligence (PROJECT-008)

## 1. Executive Testing Summary
- **Test Runner**: `pytest` 9.1.1 (Python 3.12.8)
- **Execution Date**: October 19, 2026
- **Test Scope**: API Contract Verification, ML Probability Bounds, Survival Monotonicity, Hazard Non-Negativity, SHAP Dimensionality, SQLite ACID Transactions, and Idempotent Seeding.
- **Results**: **23 Passed, 0 Failed, 0 Skipped (100% Pass Rate)**
- **Total Execution Time**: 2.88 seconds

---

## 2. Test Suite Breakdown

### 2.1 Backend API Test Suite (`source_code/tests/test_api.py` - 11 Tests)
1. `test_dashboard_home`: Verifies `/` loads the dashboard with HTTP 200 and required branding elements.
2. `test_predict_page_render`: Verifies `/predict` serves the interactive subscriber input form.
3. `test_performance_page_render`: Verifies `/model-performance` renders benchmark charts and metrics.
4. `test_history_page_render`: Verifies `/history` renders the audit ledger table.
5. `test_api_stats`: Asserts `/api/stats` outputs integer total, churn, stay, and floating-point rate.
6. `test_api_metrics`: Asserts `/api/metrics` confirms 7,043 dataset records, accuracy $\ge 0.70$, and ROC-AUC $\ge 0.80$.
7. `test_api_history`: Asserts `/api/history` delivers a JSON array of historical prediction records.
8. `test_predict_submission_high_risk_churn`: Tests POST with month-to-month, high monthly charges, and fiber optic inputs; asserts churn prediction and base64 visualization generation.
9. `test_predict_submission_low_risk_retention`: Tests POST with two-year contract and high tenure; asserts low-risk retention prediction.
10. `test_predict_database_persistence`: Verifies POST to `/predict` increments total records in SQLite database.
11. `test_invalid_input_error_handling`: Tests error-handling resilience when non-numeric values are passed to numeric fields.

### 2.2 Machine Learning Pipeline Test Suite (`source_code/tests/test_pipeline.py` - 9 Tests)
1. `test_random_forest_model_structure`: Confirms Random Forest Classifier has 1,000 estimators and `predict_proba`.
2. `test_cox_survival_model_structure`: Confirms Cox model has 22 hazard covariates and valid baseline hazard tables.
3. `test_shap_explainer_structure`: Confirms SHAP TreeExplainer is initialized and capable of computing Shapley values.
4. `test_single_prediction_probability_bounds`: Verifies that predicted probabilities sum to $1.0000 \pm 10^{-4}$ and lie strictly in $[0, 1]$.
5. `test_survival_function_monotonicity`: Asserts that the cumulative survival function $S(t)$ is monotonically non-increasing across tenure milestones ($S(t_1) \ge S(t_2)$ for $t_1 \le t_2$).
6. `test_hazard_function_non_negative`: Asserts that cumulative hazard $H(t)$ is non-negative for all tenure months.
7. `test_shap_values_dimensionality`: Asserts that SHAP values output exactly 23 feature dimensions matching model inputs.
8. `test_database_persistence_crud`: Direct unit test of `database.py` functions verifying insert, select, and filter operations.
9. `test_database_seeding_idempotence`: Asserts that `seed_database_if_empty()` is a safe no-op when records already exist.

### 2.3 Structural Audit Verification (`source_code/tests/test_audit_verification.py` - 3 Tests)
1. `test_requirements_exist`: Verifies `requirements.txt` exists at project root.
2. `test_docs_exist`: Verifies `technical_documentation.docx` exists in `docs/`.
3. `test_presentation_exists`: Verifies `project_presentation.pptx` exists in `presentations/`.

---

## 3. Pytest Execution Console Output
```bash
$ pytest project_08_customer_churn_prediction/source_code/tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.12.8, pytest-9.1.1, pluggy-1.7.0 -- /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
cachedir: .pytest_cache
rootdir: /Users/eash/Documents/antigravity/excited-borg
collected 23 items

project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_api_history PASSED [  4%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_api_metrics PASSED [  8%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_api_stats PASSED [ 13%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_dashboard_home PASSED [ 17%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_history_page_render PASSED [ 21%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_invalid_input_error_handling PASSED [ 26%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_performance_page_render PASSED [ 30%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_predict_database_persistence PASSED [ 34%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_predict_page_render PASSED [ 39%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_predict_submission_high_risk_churn PASSED [ 43%]
project_08_customer_churn_prediction/source_code/tests/test_api.py::TestCustomerChurnAPI::test_predict_submission_low_risk_retention PASSED [ 47%]
project_08_customer_churn_prediction/source_code/tests/test_audit_verification.py::TestPROJECT008::test_docs_exist PASSED [ 52%]
project_08_customer_churn_prediction/source_code/tests/test_audit_verification.py::TestPROJECT008::test_presentation_exists PASSED [ 56%]
project_08_customer_churn_prediction/source_code/tests/test_audit_verification.py::TestPROJECT008::test_requirements_exist PASSED [ 60%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_cox_survival_model_structure PASSED [ 65%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_database_persistence_crud PASSED [ 69%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_database_seeding_idempotence PASSED [ 73%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_hazard_function_non_negative PASSED [ 78%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_random_forest_model_structure PASSED [ 82%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_shap_explainer_structure PASSED [ 86%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_shap_values_dimensionality PASSED [ 91%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_single_prediction_probability_bounds PASSED [ 95%]
project_08_customer_churn_prediction/source_code/tests/test_pipeline.py::TestCustomerChurnPipeline::test_survival_function_monotonicity PASSED [100%]

======================== 23 passed, 2 warnings in 2.88s ========================
```
