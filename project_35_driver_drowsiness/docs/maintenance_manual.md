# VIGILANCE-AI Maintenance & Operator Manual

## 1. Routine Optical Sensor Calibration
- **Interval**: Bi-weekly or after cabin maintenance.
- **Procedure**: Clean Near-Infrared optical lens using optical-grade isopropyl alcohol wipes. Verify 850nm LED output using digital camera sensor.

## 2. SQLite WAL Checkpointing
The database operates in Write-Ahead Logging mode (`PRAGMA journal_mode=WAL;`).
To force a manual checkpoint:
```python
import sqlite3
conn = sqlite3.connect("driver_safety.db")
conn.execute("PRAGMA wal_checkpoint(FULL);")
conn.close()
```

## 3. Retraining Pipeline
To retrain models with updated fleet survey telemetry:
```bash
python3 source_code/backend/train_models.py
```
This updates `fatigue_classifier_weights.pt`, `vigilance_regressor_weights.pt`, `fatigue_scalers.json`, and `model_metadata.json` automatically.
