import os
import sqlite3
import datetime
from typing import Dict, Any, List, Optional

class NIDSDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "nids.db")
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    destination_ip TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    service TEXT NOT NULL,
                    flag TEXT NOT NULL,
                    src_bytes INTEGER NOT NULL,
                    dst_bytes INTEGER NOT NULL,
                    predicted_category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    is_anomaly INTEGER NOT NULL,
                    recommended_action TEXT NOT NULL,
                    latency_ms REAL NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_threat ON security_events(threat_level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON security_events(predicted_category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)")
            conn.commit()

    def log_event(self, event: Dict[str, Any]) -> int:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO security_events (
                    timestamp, source_ip, destination_ip, protocol, service, flag,
                    src_bytes, dst_bytes, predicted_category, confidence, threat_level,
                    anomaly_score, is_anomaly, recommended_action, latency_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get("timestamp", now),
                event.get("source_ip", "192.168.1.105"),
                event.get("destination_ip", "10.0.0.1"),
                event.get("protocol", "tcp"),
                event.get("service", "http"),
                event.get("flag", "SF"),
                int(event.get("src_bytes", 0)),
                int(event.get("dst_bytes", 0)),
                event.get("predicted_category", "Normal"),
                float(event.get("confidence", 0.0)),
                event.get("threat_level", "BENIGN"),
                float(event.get("anomaly_score_pct", 0.0)),
                1 if event.get("is_anomaly", False) else 0,
                event.get("recommended_action", "ALLOW"),
                float(event.get("latency_ms", 0.0))
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM security_events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_threat_analytics(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM security_events")
            total = cursor.fetchone()["total"]

            if total == 0:
                return {
                    "total_inspected_packets": 0,
                    "malicious_intrusions": 0,
                    "benign_packets": 0,
                    "anomalies_detected": 0,
                    "category_distribution": {},
                    "threat_levels": {},
                    "avg_latency_ms": 0.0
                }

            cursor.execute("""
                SELECT predicted_category, COUNT(*) as cnt
                FROM security_events
                GROUP BY predicted_category
            """)
            category_counts = {row["predicted_category"]: row["cnt"] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT threat_level, COUNT(*) as cnt
                FROM security_events
                GROUP BY threat_level
            """)
            threat_counts = {row["threat_level"]: row["cnt"] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as cnt FROM security_events WHERE is_anomaly = 1")
            anomalies = cursor.fetchone()["cnt"]

            cursor.execute("SELECT AVG(latency_ms) as avg_lat FROM security_events")
            avg_latency = cursor.fetchone()["avg_lat"]

            benign = category_counts.get("Normal", 0)
            intrusions = total - benign

            return {
                "total_inspected_packets": total,
                "malicious_intrusions": intrusions,
                "benign_packets": benign,
                "anomalies_detected": anomalies,
                "category_distribution": category_counts,
                "threat_levels": threat_counts,
                "avg_latency_ms": round(float(avg_latency or 0.0), 2)
            }
