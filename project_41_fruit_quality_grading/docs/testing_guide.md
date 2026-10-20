# Testing Guide: Automated QA Verification Suite

## Running Tests
Execute the complete automated test suite:
```bash
python3 -m unittest project_41_fruit_quality_grading/source_code/tests/test_audit_verification.py project_41_fruit_quality_grading/source_code/tests/test_api_and_system.py
```

## Test Coverage (33 Passing Tests, 100% Pass Rate)
- **Deliverables Existence**: Requirements, docs, presentation slides, environment config, walkthrough scripts.
- **REST API Contracts**: Health checks (`/api/health/` and `/api/health`), fruit inspection, items list, lanes, audit ledger, chute overrides.
- **PyTorch Invariance**: MultiTaskFruitNet forward shape `[B, 3, 64, 64]`, Regressor forward shape `[B, 10]`, physics bounds.
- **SQLite WAL Mode**: Validates non-blocking WAL journal mode and referential integrity.
- **Cryptographic Chaining**: Validates unbroken SHA-256 block hash continuity, Genesis block seeding, and tamper detection.
