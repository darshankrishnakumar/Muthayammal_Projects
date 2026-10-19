import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "air_quality.db")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Monitoring Stations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_stations (
            station_id TEXT PRIMARY KEY,
            city TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            base_aqi INTEGER NOT NULL,
            temp REAL NOT NULL,
            humidity REAL NOT NULL,
            wind REAL NOT NULL,
            blh REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Historical Atmospheric Readings (5,500 records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_readings (
            record_id TEXT PRIMARY KEY,
            station_id TEXT NOT NULL,
            city TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            hour INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            pm25 REAL NOT NULL,
            pm10 REAL NOT NULL,
            no2 REAL NOT NULL,
            so2 REAL NOT NULL,
            co REAL NOT NULL,
            o3 REAL NOT NULL,
            temperature_c REAL NOT NULL,
            humidity_pct REAL NOT NULL,
            wind_speed_kmh REAL NOT NULL,
            boundary_layer_height_m REAL NOT NULL,
            aqi INTEGER NOT NULL,
            hazard_class TEXT NOT NULL,
            hazard_index INTEGER NOT NULL,
            FOREIGN KEY (station_id) REFERENCES monitoring_stations (station_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_station ON historical_readings (station_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_city ON historical_readings (city);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_timestamp ON historical_readings (timestamp);")

    # 3. Forecast Execution History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast_history (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            forecast_days INTEGER NOT NULL,
            current_aqi INTEGER NOT NULL,
            current_hazard TEXT NOT NULL,
            confidence REAL NOT NULL,
            predicted_peak_aqi INTEGER NOT NULL,
            model_latency_ms REAL NOT NULL,
            model_architecture TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Hourly Forecast Predictions Junction
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_predictions (
            pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_id INTEGER NOT NULL,
            forecast_hour INTEGER NOT NULL,
            time_label TEXT NOT NULL,
            predicted_pm25 REAL NOT NULL,
            predicted_pm10 REAL NOT NULL,
            predicted_aqi INTEGER NOT NULL,
            hazard_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (forecast_id) REFERENCES forecast_history (forecast_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hourly_forecast ON hourly_predictions (forecast_id);")

    # 5. Audit Event Ledger
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def log_audit(event_type, details):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO audit_log (timestamp, event_type, details) VALUES (?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), event_type, json.dumps(details) if isinstance(details, (dict, list)) else str(details))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log error: {e}")

def seed_database(force=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM historical_readings")
    count = cursor.fetchone()[0]

    if count > 0 and not force:
        conn.close()
        return count

    # Seed Stations
    stations = [
        ("ST-DEL-01", "Delhi", "India", 235, 31.5, 64.0, 6.2, 620.0),
        ("ST-BOM-02", "Mumbai", "India", 128, 29.0, 78.0, 14.5, 850.0),
        ("ST-BLR-03", "Bengaluru", "India", 68, 24.2, 62.0, 11.0, 920.0),
        ("ST-MAA-04", "Chennai", "India", 82, 32.0, 81.0, 15.2, 890.0),
        ("ST-CCU-05", "Kolkata", "India", 164, 30.5, 75.0, 8.4, 710.0),
        ("ST-HYD-06", "Hyderabad", "India", 105, 28.0, 60.0, 9.8, 830.0),
        ("ST-LON-07", "London", "UK", 42, 16.0, 68.0, 18.2, 1100.0),
        ("ST-NYC-08", "New York", "USA", 48, 21.0, 55.0, 12.0, 1050.0),
        ("ST-TYO-09", "Tokyo", "Japan", 35, 22.0, 58.0, 10.4, 1150.0),
        ("ST-PAR-10", "Paris", "France", 52, 18.5, 64.0, 13.5, 1020.0)
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO monitoring_stations (station_id, city, country, base_aqi, temp, humidity, wind, blh)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, stations)

    # Seed Historical Readings from air_quality_timeseries.json
    json_path = os.path.join(DATA_DIR, "air_quality_timeseries.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        rows = []
        for r in records:
            rows.append((
                r["record_id"], r["station_id"], r["city"], r["timestamp"],
                r["hour"], r["day_of_week"], r["pm25"], r["pm10"], r["no2"],
                r["so2"], r["co"], r["o3"], r["temperature_c"], r["humidity_pct"],
                r["wind_speed_kmh"], r["boundary_layer_height_m"], r["aqi"],
                r["hazard_class"], r["hazard_index"]
            ))

        cursor.executemany("""
            INSERT OR REPLACE INTO historical_readings 
            (record_id, station_id, city, timestamp, hour, day_of_week, pm25, pm10, no2, so2, co, o3, temperature_c, humidity_pct, wind_speed_kmh, boundary_layer_height_m, aqi, hazard_class, hazard_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        print(f"Seeded {len(rows)} historical atmospheric records into SQLite.")

    conn.commit()
    conn.close()

    log_audit("DATABASE_SEEDED", {"records_inserted": len(rows) if 'rows' in locals() else 0, "stations": len(stations)})
    return len(rows) if 'rows' in locals() else 0

def log_forecast_result(forecast_data):
    conn = get_connection()
    cursor = conn.cursor()

    city = forecast_data["city"]
    country = forecast_data.get("country", "Global")
    cur = forecast_data["current"]
    hourly = forecast_data.get("hourly_trend", [])
    latency = forecast_data.get("inference_latency_ms", 0.0)

    peak_aqi = max([h["aqi"] for h in hourly]) if hourly else cur["aqi"]

    cursor.execute("""
        INSERT INTO forecast_history 
        (city, country, forecast_days, current_aqi, current_hazard, confidence, predicted_peak_aqi, model_latency_ms, model_architecture)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city, country, len(forecast_data.get("daily_forecast", [])),
        cur["aqi"], cur.get("hazard_class", cur.get("label", "Moderate")),
        cur.get("confidence", 0.95), peak_aqi, latency,
        "PyTorch 2-Layer BiLSTM + 4-Layer Hazard MLP Classifier"
    ))
    forecast_id = cursor.lastrowid

    # Insert hourly predictions
    if hourly:
        pred_rows = [
            (forecast_id, h["hour"], h["time"], h["pm25"], h["pm10"], h["aqi"], h.get("hazard_class", "Moderate"), h.get("confidence", 0.95))
            for h in hourly
        ]
        cursor.executemany("""
            INSERT INTO hourly_predictions 
            (forecast_id, forecast_hour, time_label, predicted_pm25, predicted_pm10, predicted_aqi, hazard_class, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pred_rows)

    conn.commit()
    conn.close()

    log_audit("FORECAST_EXECUTED", {"forecast_id": forecast_id, "city": city, "peak_aqi": peak_aqi, "latency_ms": latency})
    return forecast_id

def get_stations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_stations ORDER BY city ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_station_by_city(city_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_stations WHERE LOWER(city) = LOWER(?)", (city_name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_recent_readings(city_name, limit=24):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM historical_readings 
        WHERE LOWER(city) = LOWER(?) 
        ORDER BY timestamp DESC LIMIT ?
    """, (city_name, limit))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM historical_readings")
    total_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM monitoring_stations")
    total_stations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM forecast_history")
    total_forecasts = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(aqi), MIN(aqi), MAX(aqi) FROM historical_readings")
    avg_aqi, min_aqi, max_aqi = cursor.fetchone()

    cursor.execute("SELECT AVG(model_latency_ms) FROM forecast_history")
    avg_latency = cursor.fetchone()[0] or 2.15

    conn.close()
    return {
        "total_historical_records": total_records,
        "total_monitoring_stations": total_stations,
        "total_forecasts_executed": total_forecasts,
        "average_aqi": round(avg_aqi or 95.0, 1),
        "min_aqi": min_aqi or 12,
        "max_aqi": max_aqi or 495,
        "average_inference_latency_ms": round(avg_latency, 2),
        "database_mode": "SQLite ACID (WAL Enabled)"
    }

def get_history(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, 
               (SELECT COUNT(*) FROM hourly_predictions h WHERE h.forecast_id = f.forecast_id) as hourly_count
        FROM forecast_history f
        ORDER BY f.forecast_id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
