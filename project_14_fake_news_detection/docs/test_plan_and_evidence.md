# Quality Assurance Test Plan & Execution Evidence

## Execution Summary
- **Test Framework**: `pytest 9.1.1`
- **Total Tests**: 27
- **Passed**: 27 (100%)
- **Failed**: 0
- **Duration**: 3.00 seconds

## Test Breakdown

### 1. Model & NLP Unit Tests (`test_model.py` - 10 Tests)
- `test_model_and_vectorizer_loaded`: Confirms Passive-Aggressive model and TF-IDF artifacts.
- `test_vectorizer_vocabulary`: Verifies 146,627 vocabulary feature count.
- `test_stopword_removal_and_lemmatizer`: Checks WordNet morphological lemmatization.
- `test_source_watermark_stripping`: Validates regex publisher tag removal.
- `test_sensationalism_radar`: Tests detection of sensational clickbait tokens.
- `test_speculative_framing`: Checks identification of hearsay markers.
- `test_objective_journalism`: Confirms institutional journalistic keywords.
- `test_fake_news_classification`: Verifies high-confidence fake detection.
- `test_real_news_classification`: Verifies high-confidence authentic reporting.
- `test_pure_language_mode`: Verifies source-agnostic linguistic processing.

### 2. API Integration Tests (`test_api.py` - 9 Tests)
- `test_health_endpoint`: Asserts status 200, port 5014, and connected database.
- `test_home_route`: Validates landing hero page rendering.
- `test_predict_get_page`: Validates visualizer console rendering.
- `test_api_predict_fake`: Checks JSON endpoint on sensational fake text.
- `test_api_predict_real`: Checks JSON endpoint on authentic judicial reporting.
- `test_api_predict_missing_text`: Asserts error 400 for empty payloads.
- `test_api_experiments`: Validates benchmark comparison response.
- `test_api_history`: Checks historical verification log retrieval.
- `test_api_stats`: Checks aggregate statistics endpoint.

### 3. Database Subsystem Tests (`test_database.py` - 5 Tests)
- `test_db_connection`: Validates SQLite connection and schema creation.
- `test_db_init`: Confirms table existence and index integrity.
- `test_log_verification_and_retrieve`: Verifies INSERT and SELECT transactions.
- `test_database_stats`: Confirms aggregate counts and average sensationalism.
- `test_history_limit_slicing`: Tests query pagination limits.

### 4. Audit Verification Tests (`test_audit_verification.py` - 3 Tests)
- `test_docs_exist`: Confirms presence of technical documentation.
- `test_presentation_exists`: Confirms presence of 15-slide presentation.
- `test_requirements_exist`: Confirms presence of dependency file.
