# Testing Guide: Automated QA Verification Suite

## Running Tests
Execute the comprehensive automated test suite:
```bash
python3 -m unittest project_40_fire_smoke_detection/source_code/tests/test_audit_verification.py project_40_fire_smoke_detection/source_code/tests/test_api_and_system.py
```

## Test Coverage (33 Passing Tests, 100% Pass Rate)
- **Deliverables Existence**: Requirements, docs, presentation slides, environment config, walkthrough scripts.
- **REST API Contracts**: Health checks (`/api/health/` and `/api/health`), incident analysis, zones, history, audit ledger, acknowledgment, suppression dispatch.
- **PyTorch Invariance**: DualStream tensor forward shapes `[B, 3, 64, 64]` and `[B, 8]`, Regressor tensor shape `[B, 10]`, physics bounds.
- **SQLite WAL Mode**: Validates WAL journal mode and non-blocking ACID operations.
- **Cryptographic Chaining**: Validates unbroken SHA-256 block hash continuity, Genesis block seeding, and tamper detection.
