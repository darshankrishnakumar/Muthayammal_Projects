# Master Registry of Critical & High-Severity Defects

This registry documents defects discovered during the systematic source code, ML pipeline, and runtime execution audits.

| Finding ID | Project ID | Severity | File Path | Component | Description & Impact | Reproduction Method | Remediation Status |
|---|---|---|---|---|---|---|---|
| FIND-001 | PROJECT-003 | HIGH | `tests/test_pipeline.py` | PyTorch Hub / MobileNetV2 | SSL certificate validation failure on macOS Python 3.12 (`[SSL: CERTIFICATE_VERIFY_FAILED]`) blocking model weight download. | Executed `python3 tests/test_pipeline.py` | RESOLVED (Patched SSL default context with `certifi` CA bundle). |
| FIND-002 | PROJECT-004 | HIGH | `scripts/train_model.py` | Training Pipeline | Relative path resolution failure when executed outside project root, causing `FileNotFoundError: car_data.csv`. | Executed `python3 scripts/train_model.py` | RESOLVED (Converted to dynamic base-relative paths). |
| FIND-003 | PROJECT-005 | HIGH | `requirements.txt` | Dependency Management | Missing `xgboost` dependency causing `ImportError` on multi-class career classification model. | Executed `python3 test_model.py` | RESOLVED (Installed `xgboost>=3.0.0` in Python environment). |
| FIND-004 | PROJECT-007 | HIGH | `requirements.txt` | Dependency Management | Missing `flask_cors` and `pytest` packages preventing API test execution. | Executed `pytest tests/` | RESOLVED (Installed `flask_cors` and `pytest`). |
| FIND-005 | PROJECT-018 | HIGH | `config.py` & `backend/gbm_recommender.py` | Recommendation Engine | Schema column discrepancy (`outfit_id` vs `item_id`) and dictionary-wrapped pipeline causing `'dict' has no attribute 'predict'`. | Executed `python3 test_all.py` | RESOLVED (Harmonized catalogue column aliases and updated `load_model` to unpack dictionary pipelines). |
| FIND-006 | PROJECT-038 | HIGH | `backend/app/db/session.py` | Database Integration | Missing `sqlalchemy` dependency causing `ModuleNotFoundError` during FastAPI startup. | Executed `python3 -m unittest backend/tests/test_api.py` | RESOLVED (Installed `sqlalchemy>=2.0.0`). |

