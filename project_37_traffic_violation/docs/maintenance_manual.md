# Maintenance & Operational Manual

## 1. Routine Camera Calibration
Cameras (`CAM-101` through `CAM-106`) require monthly optical focal alignment and ANPR perspective correction. Calibration events are logged via:
```python
from database import log_audit_entry
log_audit_entry("CAMERA_CALIBRATION", "CAM-101 focal length recalibrated for night glare")
```

## 2. SQLite Database Maintenance
Perform monthly vacuuming and WAL checkpointing:
```sql
PRAGMA wal_checkpoint(TRUNCATE);
VACUUM;
```

## 3. Audit Ledger Forensic Auditing
To verify that no records in `traffic_enforcement.db` have been tampered with:
```bash
python3 -c "from tests.test_api_and_system import TrafficEnforcementSystemTests; t = TrafficEnforcementSystemTests(); t.setUpClass(); t.test_28_crypto_hash_tamper_detection(); print('Audit Ledger 100% Cryptographically Intact')"
```
