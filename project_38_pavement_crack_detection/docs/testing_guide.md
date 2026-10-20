# Testing Guide: Automated QA Verification Suite

## Running Tests
Execute the complete dual-runner test suite:
```bash
python3 -m unittest test_audit_verification.py test_api_and_system.py
```

## Test Coverage
- **Deliverables Existence**: Verifies dataset, weights, database, slides, docs.
- **REST API Contracts**: Health checks (`/api/health/` and `/api/health`), analysis, work orders, audit logs.
- **PyTorch Invariance**: Tensor shape verification, gradient detachment, value bounding.
- **SQLite WAL Mode**: Validates WAL journal mode and referential integrity.
- **Cryptographic Chaining**: End-to-end block hash continuity and tamper rejection.
