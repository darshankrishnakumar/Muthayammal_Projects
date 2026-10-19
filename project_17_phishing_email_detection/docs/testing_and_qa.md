# Automated Verification & Quality Assurance Suite

## Test Architecture
The test suite is partitioned into two test files within `source_code/tests/`:
1. `test_system_and_ml.py`: 20 unit, neural, algorithmic, and integration tests.
2. `test_audit_verification.py`: 3 repository structure, presentation, and documentation tests.

## Running the Automated Test Suite

```bash
python3 -m unittest discover -s project_17_phishing_email_detection/source_code/tests -v
```

## Test Results: 23 Passing Tests (100% Pass Rate)

| # | Test Name | Target Component | Status |
|---|---|---|---|
| 1 | `test_requirements_exist` | Repository Integrity | PASS |
| 2 | `test_docs_exist` | Documentation Verification | PASS |
| 3 | `test_presentation_exists` | Presentation Verification | PASS |
| 4 | `test_rcnn_model_initialization` | Neural Architecture | PASS |
| 5 | `test_attention_layer_softmax_sum` | Attention Softmax Math | PASS |
| 6 | `test_multilevel_tensor_shapes` | Character & Word Tensors | PASS |
| 7 | `test_rcnn_forward_pass_execution` | Forward Pass Bounding | PASS |
| 8 | `test_header_feature_extraction` | 8-Dim Header Extractor | PASS |
| 9 | `test_baseline_models_availability` | 8 Baselines Instantiation | PASS |
| 10 | `test_phishing_detection_bank_sample` | End-to-End Threat Detection | PASS |
| 11 | `test_legitimate_detection_corporate_sync` | False Alarm Mitigation | PASS |
| 12 | `test_attention_heatmap_generation` | XAI Heatmap Generator | PASS |
| 13 | `test_sqlite_database_tables_and_columns` | SQLite Schema Verification | PASS |
| 14 | `test_sqlite_historical_seeding` | Database Seeding | PASS |
| 15 | `test_unbalanced_dataset_guarantee_metrics` | Specificity Metric Bounds | PASS |
| 16 | `test_api_health_endpoint` | Health Endpoint Schema | PASS |
| 17 | `test_api_benchmark_endpoint` | Benchmark Endpoint Schema | PASS |
| 18 | `test_api_samples_endpoint` | Preset Samples Schema | PASS |
| 19 | `test_api_history_endpoint` | SQLite History Retrieval | PASS |
| 20 | `test_api_stats_endpoint` | Aggregate Telemetry API | PASS |
| 21 | `test_api_predict_empty_content_validation` | Input Validation 400 | PASS |
| 22 | `test_api_predict_live_inference_and_db_logging` | Live Ingestion & ACID Log | PASS |
| 23 | `test_ensemble_model_selection` | Multi-Model Consensus | PASS |
