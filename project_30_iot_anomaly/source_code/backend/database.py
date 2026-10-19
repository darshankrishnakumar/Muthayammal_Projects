"""
AI-Based IoT Device Anomaly Detection for Smart Home Security
Relational SQLite Database Layer with ACID Persistence & WAL Mode
"""

import os
import sqlite3
import json
from datetime import datetime, timezone, timedelta
import random

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "iot_security.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS iot_devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        ip_address TEXT NOT NULL,
        protocol TEXT NOT NULL,
        norm_packet INTEGER NOT NULL,
        norm_rate REAL NOT NULL,
        icon TEXT NOT NULL,
        role TEXT NOT NULL,
        quarantine_status TEXT DEFAULT 'ONLINE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS network_traffic_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flow_id TEXT UNIQUE NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        device_name TEXT NOT NULL,
        packet_size_bytes REAL NOT NULL,
        packet_rate_pps REAL NOT NULL,
        syn_ratio REAL NOT NULL,
        payload_entropy REAL NOT NULL,
        conn_freq_hz REAL NOT NULL,
        byte_rate_bps REAL NOT NULL,
        port_diversity REAL NOT NULL,
        retransmission_rate REAL NOT NULL,
        FOREIGN KEY (device_name) REFERENCES iot_devices(name)
    );

    CREATE TABLE IF NOT EXISTS anomaly_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        device_name TEXT NOT NULL,
        is_anomaly BOOLEAN NOT NULL,
        attack_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        color TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        anomaly_score INTEGER NOT NULL,
        reconstruction_error REAL NOT NULL,
        quarantine_status TEXT NOT NULL,
        telemetry_json TEXT NOT NULL,
        FOREIGN KEY (device_name) REFERENCES iot_devices(name)
    );

    CREATE TABLE IF NOT EXISTS quarantine_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        device_name TEXT NOT NULL,
        action_type TEXT NOT NULL,
        justification TEXT NOT NULL,
        threat_signature TEXT NOT NULL,
        mitigation_rule TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_inspect_timestamp ON anomaly_inspections(timestamp);
    CREATE INDEX IF NOT EXISTS idx_inspect_device ON anomaly_inspections(device_name);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """)

    conn.commit()
    conn.close()

def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM iot_devices")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    devices = [
        ('Smart IP Camera', '192.168.1.42', 'RTSP / TCP', 1240, 45, '📹', 'Living Room Cam', 'ONLINE'),
        ('Smart Thermostat', '192.168.1.18', 'MQTT / TLS', 180, 2, '🌡️', 'HVAC Control Node', 'ONLINE'),
        ('Smart Lock', '192.168.1.105', 'Zigbee / BLE Gateway', 64, 0.5, '🔐', 'Front Entrance Deadbolt', 'ONLINE'),
        ('Smart TV 4K', '192.168.1.88', 'HTTPS / SSDP', 1420, 120, '📺', 'Media Room OLED', 'ONLINE'),
        ('Edge Wi-Fi Router', '192.168.1.1', 'DNS / DHCP / NTP', 512, 250, '📡', 'Core Gateway', 'ONLINE'),
        ('Smart Voice Assistant', '192.168.1.73', 'mDNS / WebSockets', 320, 15, '🔊', 'Kitchen Assistant', 'ONLINE')
    ]

    for d in devices:
        cursor.execute("""
            INSERT INTO iot_devices (name, ip_address, protocol, norm_packet, norm_rate, icon, role, quarantine_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, d)

    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity)
        VALUES (?, 'SYSTEM_INIT', 'IoT Security SQLite schema initialized with WAL mode and 6 registered devices.', 'INFO')
    """, (now_iso,))

    conn.commit()
    conn.close()

def log_inspection(data):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO anomaly_inspections
        (timestamp, device_name, is_anomaly, attack_type, severity, color, action_taken, anomaly_score, reconstruction_error, quarantine_status, telemetry_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_iso,
        data['device'],
        int(data['is_anomaly']),
        data['attack_type'],
        data['severity'],
        data['color'],
        data['action_taken'],
        data['anomaly_score'],
        data['reconstruction_error'],
        data['quarantine_status'],
        json.dumps(data.get('telemetry', {}))
    ))
    inserted_id = cursor.lastrowid

    # If critical quarantine triggered, update device status and log quarantine action
    if data['quarantine_status'] == 'ISOLATED':
        cursor.execute("UPDATE iot_devices SET quarantine_status = 'ISOLATED' WHERE name = ?", (data['device'],))
        cursor.execute("""
            INSERT INTO quarantine_actions (timestamp, device_name, action_type, justification, threat_signature, mitigation_rule)
            VALUES (?, ?, 'QUARANTINE_ISOLATE', 'Reconstruction error exceeded critical threshold', ?, ?)
        """, (now_iso, data['device'], data['attack_type'], data['action_taken']))
        cursor.execute("""
            INSERT INTO audit_log (timestamp, event_type, details, severity)
            VALUES (?, 'DEVICE_QUARANTINED', ?, 'CRITICAL')
        """, (now_iso, f"Device '{data['device']}' quarantined due to {data['attack_type']}."))
    else:
        cursor.execute("""
            INSERT INTO audit_log (timestamp, event_type, details, severity)
            VALUES (?, 'TRAFFIC_INSPECTED', ?, 'INFO')
        """, (now_iso, f"Traffic analyzed for '{data['device']}': {data['attack_type']} (Score: {data['anomaly_score']})."))

    conn.commit()
    conn.close()
    return inserted_id

def set_device_quarantine(device_name, status):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("UPDATE iot_devices SET quarantine_status = ? WHERE name = ?", (status, device_name))
    cursor.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity)
        VALUES (?, 'QUARANTINE_OVERRIDE', ?, 'WARNING')
    """, (now_iso, f"Manual quarantine status for '{device_name}' updated to '{status}'."))
    conn.commit()
    conn.close()

def get_recent_inspections(limit=40):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ai.*, d.ip_address, d.protocol, d.icon, d.role
        FROM anomaly_inspections ai
        LEFT JOIN iot_devices d ON ai.device_name = d.name
        ORDER BY ai.timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            'id': r['id'],
            'timestamp': r['timestamp'],
            'device': r['device_name'],
            'ip_address': r['ip_address'],
            'protocol': r['protocol'],
            'device_icon': r['icon'],
            'device_role': r['role'],
            'is_anomaly': bool(r['is_anomaly']),
            'attack_type': r['attack_type'],
            'severity': r['severity'],
            'color': r['color'],
            'action_taken': r['action_taken'],
            'anomaly_score': r['anomaly_score'],
            'reconstruction_error': r['reconstruction_error'],
            'quarantine_status': r['quarantine_status'],
            'telemetry': json.loads(r['telemetry_json'])
        })
    conn.close()
    return results

def get_all_devices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iot_devices ORDER BY id ASC")
    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results

def get_security_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM anomaly_inspections")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomaly_inspections WHERE is_anomaly = 1")
    anomalies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomaly_inspections WHERE severity = 'CRITICAL'")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(anomaly_score) FROM anomaly_inspections")
    avg_score = cursor.fetchone()[0] or 18.0

    cursor.execute("SELECT COUNT(*) FROM iot_devices WHERE quarantine_status = 'ISOLATED'")
    isolated_devs = cursor.fetchone()[0]

    conn.close()
    avg_score = round(avg_score, 1)
    security_index = max(10, min(100, int(100 - avg_score * 0.75)))

    return {
        'total_inspections': total,
        'anomalies_detected': anomalies,
        'critical_threats': critical,
        'isolated_devices': isolated_devs,
        'avg_anomaly_score': avg_score,
        'system_security_index': security_index
    }

def get_audit_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results

def verify_wal_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM iot_devices;")
    dev_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM anomaly_inspections;")
    insp_count = cursor.fetchone()[0]
    conn.close()
    return {
        'journal_mode': mode.upper(),
        'wal_enabled': mode.upper() == 'WAL',
        'devices_count': dev_count,
        'inspections_count': insp_count
    }

if __name__ == '__main__':
    seed_database()
    print("Database seeded and WAL status verified:")
    print(verify_wal_status())
