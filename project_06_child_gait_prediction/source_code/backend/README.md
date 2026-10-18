# Child Gait Prediction Backend & Data Pipeline

Backend persistence and REST API layer for the Child Gait Prediction project.
Separates the database layer from the ML model, supporting development with synthetic datasets and immediate drop-in replacement with real datasets.

---

## 🗄️ Database Architecture

- **Database Engine**: SQLite (`backend/database/gait_database.db`)
- **Primary Table**: `gait_records`

### `gait_records` Schema:

| Column Name | SQL Type | Description |
|---|---|---|
| `id` | `TEXT PRIMARY KEY` | Unique record identifier (UUID / timestamp) |
| `child_id` | `TEXT NOT NULL` | Identifier for the child (e.g. `C-101`) |
| `age` | `INTEGER NOT NULL` | Age of child in years (1–18) |
| `gender` | `TEXT NOT NULL` | Child gender (`Male`, `Female`) |
| `heel_pressure` | `REAL NOT NULL` | Peak heel pressure (kPa) |
| `toe_pressure` | `REAL NOT NULL` | Peak toe pressure (kPa) |
| `tilt_angle` | `REAL NOT NULL` | Foot tilt angle (°) |
| `step_duration` | `REAL NOT NULL` | Step duration in seconds |
| `stride_length` | `REAL NOT NULL` | Stride length in cm |
| `walking_speed` | `REAL NOT NULL` | Walking speed in m/s |
| `gait_class` | `TEXT NOT NULL` | Classification (`Normal`, `Diplegic`, `Hemiplegic`) |
| `confidence` | `REAL NULL` | Optional model confidence score |
| `created_at` | `TIMESTAMP` | Timestamp of assessment entry |

---

## 🚀 How to Start the Backend and Database

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install fastapi uvicorn pydantic
```

### 2. Run the Server
From the project root:
```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
The database file `backend/database/gait_database.db` and `gait_records` table are **automatically created on startup**.

Interactive API Swagger documentation is available at:
👉 **http://localhost:8000/docs**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & database connection status |
| `POST` | `/api/import-csv` | Import CSV dataset into `gait_records` table |
| `POST` | `/api/records` | Add a new gait assessment record |
| `POST` | `/api/predict` | Predict gait and persist assessment in `gait_records` |
| `GET` | `/api/records` | Retrieve all gait assessment records |
| `GET` | `/api/records/child/{child_id}` | Retrieve gait records for a specific child ID |
| `DELETE`| `/api/records/{record_id}` | Delete a record by ID |

---

## 📥 Importing CSV Data

To import the development dummy dataset:
```bash
curl -X POST http://localhost:8000/api/import-csv
```

To import a custom/real dataset file:
```bash
curl -X POST "http://localhost:8000/api/import-csv?filepath=/path/to/real_gait_data.csv"
```

---

## 🔄 Replacing Synthetic Dataset With Real Data Later

1. Place your real dataset CSV in `backend/data/real_gait_data.csv` (or any path).
2. Ensure columns match or map to the 9 standard fields (`child_id`, `age`, `gender`, `heel_pressure`, `toe_pressure`, `tilt_angle`, `step_duration`, `stride_length`, `walking_speed`, `gait_class`).
3. Call `POST /api/import-csv?filepath=backend/data/real_gait_data.csv`.
4. The database table `gait_records` will directly store and index the real data with zero architectural code changes needed.

---

## ⚕️ Medical Safety Disclaimer
*IMPORTANT: The synthetic dataset is provided for development and testing of the pipeline only. It is not clinically validated. This application is a college-level machine learning prototype intended for educational and decision-support purposes and does not replace professional medical diagnosis, clinical assessment, or treatment.*
