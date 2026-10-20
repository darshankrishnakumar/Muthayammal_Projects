# SORT-AI Maintenance & Operator Manual

## 1. Routine Optical Inspection & Cleaning
- **Interval**: Shift change (every 8 hours).
- **Procedure**: Blow dry compressed air across Near-Infrared lens and halogen illumination array. Clean glass window with lint-free optical wipes.

## 2. Pneumatic Air Jet Solenoid Testing
- **Interval**: Weekly.
- **Procedure**: Verify valve manifold pressure is maintained at 6.0 +/- 0.3 bar. Cycle each of the 64 pneumatic solenoid valves in diagnostic mode.

## 3. SQLite Database Maintenance
Force a WAL checkpoint:
```python
import sqlite3
conn = sqlite3.connect("waste_sorting.db")
conn.execute("PRAGMA wal_checkpoint(FULL);")
conn.close()
```
