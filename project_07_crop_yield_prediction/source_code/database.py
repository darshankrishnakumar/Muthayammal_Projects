"""
CropAI — SQLite Database Layer for Prediction History
======================================================
Provides persistent storage for crop yield predictions and classifications.
Database file: cropai_history.db
"""
import io
import csv
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent / "cropai_history.db"


@contextmanager
def db_session(db_path=None):
    """Context manager ensuring transactions commit and connection closes."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=None):
    """Initializes the database schema if not already present."""
    with db_session(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                task_type TEXT NOT NULL, -- 'regression' | 'classification'
                country TEXT NOT NULL,
                crop TEXT NOT NULL,
                year INTEGER NOT NULL,
                rainfall REAL NOT NULL,
                pesticides REAL NOT NULL,
                temperature REAL NOT NULL,
                model_name TEXT NOT NULL,
                predicted_yield REAL,
                yield_unit TEXT,
                yield_tonnes_per_ha REAL,
                farm_area REAL,
                farm_area_unit TEXT,
                farm_area_ha REAL,
                total_harvest_tonnes REAL,
                classification_label TEXT,
                classification_class INTEGER,
                classification_type TEXT
            );
        """)


def save_prediction(
    task_type,
    country,
    crop,
    year,
    rainfall,
    pesticides,
    temperature,
    model_name,
    predicted_yield=None,
    yield_unit="hg/ha",
    yield_tonnes_per_ha=None,
    farm_area=None,
    farm_area_unit=None,
    farm_area_ha=None,
    total_harvest_tonnes=None,
    classification_label=None,
    classification_class=None,
    classification_type=None,
    db_path=None
):
    """Saves a prediction entry to SQLite database using parameterized query."""
    init_db(db_path)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    query = """
        INSERT INTO prediction_history (
            timestamp, task_type, country, crop, year, rainfall, pesticides,
            temperature, model_name, predicted_yield, yield_unit,
            yield_tonnes_per_ha, farm_area, farm_area_unit, farm_area_ha,
            total_harvest_tonnes, classification_label, classification_class,
            classification_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        now_str, task_type, country, crop, int(year), float(rainfall),
        float(pesticides), float(temperature), model_name,
        float(predicted_yield) if predicted_yield is not None else None,
        yield_unit,
        float(yield_tonnes_per_ha) if yield_tonnes_per_ha is not None else None,
        float(farm_area) if farm_area is not None else None,
        farm_area_unit,
        float(farm_area_ha) if farm_area_ha is not None else None,
        float(total_harvest_tonnes) if total_harvest_tonnes is not None else None,
        classification_label,
        int(classification_class) if classification_class is not None else None,
        classification_type
    )
    with db_session(db_path) as conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid


def get_history(limit=50, db_path=None):
    """Retrieves recent predictions ordered descending by ID."""
    init_db(db_path)
    query = "SELECT * FROM prediction_history ORDER BY id DESC LIMIT ?"
    with db_session(db_path) as conn:
        cursor = conn.execute(query, (int(limit),))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_prediction_by_id(pred_id, db_path=None):
    """Retrieves a single prediction by its primary key."""
    init_db(db_path)
    query = "SELECT * FROM prediction_history WHERE id = ?"
    with db_session(db_path) as conn:
        cursor = conn.execute(query, (int(pred_id),))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_prediction(pred_id, db_path=None):
    """Deletes a specific prediction by ID."""
    init_db(db_path)
    query = "DELETE FROM prediction_history WHERE id = ?"
    with db_session(db_path) as conn:
        cursor = conn.execute(query, (int(pred_id),))
        return cursor.rowcount > 0


def clear_history(db_path=None):
    """Deletes all entries from the history table."""
    init_db(db_path)
    with db_session(db_path) as conn:
        conn.execute("DELETE FROM prediction_history")
        return True


def export_history_csv(db_path=None):
    """Exports all predictions to a CSV formatted string."""
    init_db(db_path)
    query = "SELECT * FROM prediction_history ORDER BY id DESC"
    with db_session(db_path) as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()

    output = io.StringIO()
    if not rows:
        return ""

    headers = rows[0].keys()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))

    return output.getvalue()
