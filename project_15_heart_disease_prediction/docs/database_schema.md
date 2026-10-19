# Database Schema: Patient Assessment Registry

## Database Engine
SQLite3 file: `source_code/heart_patients.db`.

## Table: `patient_assessments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique patient consultation ID |
| `age` | INTEGER | NOT NULL | Patient age in years |
| `sex` | INTEGER | NOT NULL | Biological sex (0: Female, 1: Male) |
| `chest_pain_type` | INTEGER | NOT NULL | Chest pain encoding (0-3) |
| `resting_bp` | INTEGER | NOT NULL | Resting blood pressure (mm Hg) |
| `cholesterol` | INTEGER | NOT NULL | Serum cholesterol (mg/dL) |
| `fasting_bs` | INTEGER | NOT NULL | Fasting blood sugar (>120 mg/dL: 1, ≤120: 0) |
| `resting_ecg` | INTEGER | NOT NULL | Resting ECG category (0-2) |
| `max_hr` | INTEGER | NOT NULL | Maximum achieved heart rate |
| `exercise_angina`| INTEGER | NOT NULL | Exercise-induced angina (0/1) |
| `oldpeak` | REAL | NOT NULL | ST depression (mm) |
| `st_slope` | INTEGER | NOT NULL | ST slope category (0-2) |
| `prediction` | INTEGER | NOT NULL | Model verdict (0: No Disease, 1: Disease) |
| `risk_probability`| REAL | NOT NULL | Calibrated percentage probability (0-100) |
| `risk_tier` | TEXT | NOT NULL | Low, Moderate, Elevated, or High |
| `timestamp` | TEXT | NOT NULL | ISO 8601 UTC timestamp |

## Indexes
- `idx_heart_timestamp`: B-tree index on `timestamp DESC` for rapid clinical timeline queries.
