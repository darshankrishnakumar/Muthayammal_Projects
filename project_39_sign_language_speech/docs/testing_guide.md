# Testing Guide: Automated QA Verification Suite

## Running Tests
Execute the complete dual-runner test suite:
```bash
python3 -m unittest project_39_sign_language_speech/source_code/tests/test_audit_verification.py project_39_sign_language_speech/source_code/tests/test_api_and_system.py
```

## Test Coverage
- **Deliverables Existence**: Requirements, docs, slides, environment config, walkthrough scripts.
- **REST API Contracts**: Health checks (`/api/health/` and `/api/health`), prediction, logs, vocabulary, audit ledger.
- **PyTorch Invariance**: BiLSTM tensor shape `[B, 30, 54]`, attention normalization (sum=1.0), prosody physical bounds.
- **SQLite WAL Mode**: Validates WAL journal mode and referential integrity.
- **Cryptographic Chaining**: Validates unbroken SHA-256 block hash continuity and tamper detection.
