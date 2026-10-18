"""
Repository for CRUD operations on the `gait_records` table.
"""

import os
import uuid
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
from .database import get_db_connection


def record_from_row(row) -> Dict[str, Any]:
    """Converts a SQLite Row into a dictionary."""
    return {
        "id": row["id"],
        "child_id": row["child_id"],
        "childId": row["child_id"],  # frontend camelCase convenience
        "age": int(row["age"]),
        "gender": row["gender"],
        "heel_pressure": float(row["heel_pressure"]),
        "heelPressure": float(row["heel_pressure"]),
        "toe_pressure": float(row["toe_pressure"]),
        "toePressure": float(row["toe_pressure"]),
        "tilt_angle": float(row["tilt_angle"]),
        "tiltAngle": float(row["tilt_angle"]),
        "step_duration": float(row["step_duration"]),
        "stepDuration": float(row["step_duration"]),
        "stride_length": float(row["stride_length"]),
        "strideLength": float(row["stride_length"]),
        "walking_speed": float(row["walking_speed"]),
        "walkingSpeed": float(row["walking_speed"]),
        "gait_class": row["gait_class"],
        "prediction": row["gait_class"],  # frontend consistency
        "confidence": float(row["confidence"]) if row["confidence"] is not None else None,
        "data_source": row["data_source"] if "data_source" in row.keys() else "real",
        "created_at": row["created_at"],
        "date": row["created_at"],  # frontend consistency
    }


def insert_gait_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a single gait assessment record into `gait_records`."""
    record_id = data.get("id") or f"gait-{uuid.uuid4().hex[:10]}"
    created_at = data.get("created_at") or datetime.now().isoformat()
    data_source = data.get("data_source") or "real"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO gait_records (
            id, child_id, age, gender, heel_pressure, toe_pressure,
            tilt_angle, step_duration, stride_length, walking_speed,
            gait_class, confidence, data_source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id,
        str(data.get("child_id") or data.get("childId")),
        int(data.get("age")),
        str(data.get("gender")),
        float(data.get("heel_pressure") or data.get("heelPressure", 0.0)),
        float(data.get("toe_pressure") or data.get("toePressure", 0.0)),
        float(data.get("tilt_angle") or data.get("tiltAngle")),
        float(data.get("step_duration") or data.get("stepDuration")),
        float(data.get("stride_length") or data.get("strideLength")),
        float(data.get("walking_speed") or data.get("walkingSpeed")),
        str(data.get("gait_class") or data.get("prediction")),
        data.get("confidence"),
        data_source,
        created_at,
    ))

    conn.commit()
    conn.close()

    return get_gait_record_by_id(record_id)  # type: ignore


def get_gait_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single gait record by its primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gait_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return record_from_row(row) if row else None


def get_gait_records(child_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all gait records or records for a specific child ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if child_id:
        cursor.execute(
            "SELECT * FROM gait_records WHERE LOWER(child_id) = LOWER(?) ORDER BY created_at DESC",
            (child_id.strip(),)
        )
    else:
        cursor.execute("SELECT * FROM gait_records ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [record_from_row(r) for r in rows]


def delete_gait_record(record_id: str) -> bool:
    """Deletes a gait assessment record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gait_records WHERE id = ?", (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def import_csv_to_database(csv_path: str) -> Dict[str, Any]:
    """
    Parses a child gait CSV and inserts records into `gait_records`.
    Validates required fields before insertion.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    imported_count = 0
    errors = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            try:
                # Handle varying header formats (snake_case or capitalized with spaces)
                def get_field(keys, default=None):
                    for k in keys:
                        for row_k, v in row.items():
                            if row_k and row_k.strip().lower().replace(" ", "_") == k.lower():
                                return v
                    return default

                child_id = get_field(["child_id", "childid", "id"])
                age = get_field(["age"])
                gender = get_field(["gender"], default="Unspecified")
                heel = get_field(["heel_pressure", "heelpressure"])
                toe = get_field(["toe_pressure", "toepressure"])
                tilt = get_field(["tilt_angle", "tiltangle"])
                duration = get_field(["step_duration", "stepduration"])
                stride = get_field(["stride_length", "stridelength"])
                speed = get_field(["walking_speed", "walkingspeed", "speed"])
                gait_class = get_field(["gait_class", "gait_pattern", "label", "prediction", "class"])

                if not child_id or not age or not heel or not toe or not tilt or not duration or not stride or not speed:
                    errors.append(f"Row {idx}: Missing required gait parameter fields.")
                    continue

                if not gait_class:
                    gait_class = "Normal"

                record = {
                    "id": f"imported-{uuid.uuid4().hex[:8]}",
                    "child_id": str(child_id).strip(),
                    "age": int(float(age)),
                    "gender": str(gender).strip(),
                    "heel_pressure": float(heel),
                    "toe_pressure": float(toe),
                    "tilt_angle": float(tilt),
                    "step_duration": float(duration),
                    "stride_length": float(stride),
                    "walking_speed": float(speed),
                    "gait_class": str(gait_class).strip(),
                    "confidence": None,
                    "created_at": datetime.now().isoformat(),
                }
                insert_gait_record(record)
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

    return {
        "status": "success",
        "imported_count": imported_count,
        "errors": errors,
        "dataset_file": os.path.basename(csv_path),
    }
