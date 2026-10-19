import sqlite3
import os
import json
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weapon_detection.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            camera_id TEXT NOT NULL,
            threat_level TEXT NOT NULL,
            weapon_detected INTEGER NOT NULL,
            weapon_class TEXT,
            confidence REAL,
            status TEXT NOT NULL,
            notes TEXT,
            detections_json TEXT,
            image_metrics_json TEXT
        )
    """)

    # 2. CCTV Cameras table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cctv_cameras (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            zone TEXT NOT NULL,
            resolution TEXT NOT NULL,
            status TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    # 3. Threat Definitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_definitions (
            weapon_class TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            threat_level TEXT NOT NULL,
            color_code TEXT NOT NULL,
            response_protocol TEXT NOT NULL
        )
    """)

    # 4. System Audit Log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            user_id TEXT DEFAULT 'SEC-OPERATOR',
            details TEXT
        )
    """)

    # Seed Cameras if empty
    cursor.execute("SELECT COUNT(*) FROM cctv_cameras")
    if cursor.fetchone()[0] == 0:
        cameras = [
            ('CAM-01', 'North Terminal - Concourse A', 'Terminal 2 Level 1', 'Public Screening Zone', '1080p @ 30fps', 'ONLINE', 'Optical PTZ'),
            ('CAM-02', 'Baggage Screening & Cargo Belt', 'Sub-Level Baggage Hall', 'Restricted Cargo Area', '4K @ 60fps', 'ONLINE', 'X-Ray / Thermal Multi-Spectrum'),
            ('CAM-03', 'Gate 4 - Perimeter Checkpoint', 'Outer Perimeter Fence', 'Vehicle Access Gate', '1080p @ 30fps', 'ONLINE', 'Night-Vision IR Camera'),
            ('CAM-04', 'VIP Concourse & Executive Lounge', 'Terminal 1 Level 3', 'High Security Sector', '1080p @ 30fps', 'ONLINE', 'Concealed Dome Camera')
        ]
        cursor.executemany("INSERT INTO cctv_cameras VALUES (?, ?, ?, ?, ?, ?, ?)", cameras)

    # Seed Threat Definitions if empty
    cursor.execute("SELECT COUNT(*) FROM threat_definitions")
    if cursor.fetchone()[0] == 0:
        threats = [
            ('handgun', 'Firearm', 'CRITICAL', '#ff0033', 'TACTICAL PROTOCOL ALPHA: Deploy Armed Response Unit instantly. Isolate concourse sector.'),
            ('assault_rifle', 'Long Firearm', 'CRITICAL', '#ff1744', 'LETHAL THREAT PROTOCOL: Complete facility lockdown. Notify National Counter-Terror Command.'),
            ('knife', 'Bladed Weapon', 'HIGH', '#ff9100', 'CLOSE-QUARTER THREAT: Security guards intercept with ballistic shields and non-lethal taser.'),
            ('explosive', 'IED / Explosive', 'CRITICAL', '#d500f9', 'EXPLOSIVE HAZARD PROTOCOL: 300m radius evacuation. Deploy robotic ordnance disposal unit.'),
            ('holster', 'Tactical Gear', 'MEDIUM', '#ffd600', 'SUSPICIOUS GEAR: Verify diplomatic escort credentials. Shadow target on visual CCTV net.')
        ]
        cursor.executemany("INSERT INTO threat_definitions VALUES (?, ?, ?, ?, ?)", threats)

    # Seed Historical Incidents if empty
    cursor.execute("SELECT COUNT(*) FROM incidents")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).timestamp()
        sample_scenarios = [
            ('INC-0001', 'CAM-01', 'knife', 0.932, 'Bladed Weapon', 'HIGH', 'RESOLVED', 'Confiscated at security bag check', -75),
            ('INC-0002', 'CAM-03', 'handgun', 0.965, 'Firearm', 'CRITICAL', 'SECURITY_DISPATCHED', 'Armed patrol interdicted suspect at gate', -45),
            ('INC-0003', 'CAM-02', 'explosive', 0.887, 'IED / Explosive', 'CRITICAL', 'UNDER_REVIEW', 'Bomb disposal unit deployed to cargo scanner', -25),
            ('INC-0004', 'CAM-04', 'holster', 0.741, 'Tactical Gear', 'MEDIUM', 'RESOLVED', 'Authorized diplomat security escort confirmed', -15),
            ('INC-0005', 'CAM-01', None, 0.0, 'None', 'SAFE', 'RESOLVED', 'Routine civilian passenger clearance', -8),
        ]
        for inc_id, cam, w_class, conf, cat, sev, status, notes, min_offset in sample_scenarios:
            t_stamp = datetime.fromtimestamp(now + min_offset * 60, tz=timezone.utc).isoformat()
            dets = []
            if w_class:
                dets.append({
                    'id': f"det-{uuid.uuid4().hex[:6]}",
                    'class': w_class,
                    'category': cat,
                    'confidence': conf,
                    'severity': sev,
                    'bbox': {'x': 180, 'y': 110, 'width': 120, 'height': 150}
                })
            metrics = {'sharpness': 184.2, 'contrast': 64.1, 'brightness': 128.5}
            cursor.execute(
                "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (inc_id, t_stamp, cam, sev, 1 if dets else 0, w_class, conf, status, notes, json.dumps(dets), json.dumps(metrics))
            )

    conn.commit()
    conn.close()

def add_incident(inc):
    conn = get_connection()
    cursor = conn.cursor()
    dets_json = json.dumps(inc.get('detections', []))
    metrics_json = json.dumps(inc.get('image_metrics', {}))
    cursor.execute("""
        INSERT OR REPLACE INTO incidents (id, timestamp, camera_id, threat_level, weapon_detected, weapon_class, confidence, status, notes, detections_json, image_metrics_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inc['id'],
        inc.get('timestamp', datetime.now(timezone.utc).isoformat()),
        inc.get('camera_id', 'CAM-01'),
        inc.get('alert_level', 'SAFE'),
        1 if inc.get('weapon_detected') else 0,
        inc.get('detections', [{}])[0].get('class') if inc.get('detections') else None,
        inc.get('detections', [{}])[0].get('confidence', 0.0) if inc.get('detections') else 0.0,
        inc.get('status', 'UNDER_REVIEW'),
        inc.get('notes', ''),
        dets_json,
        metrics_json
    ))
    conn.commit()
    conn.close()

def get_all_incidents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        dets = json.loads(r['detections_json']) if r['detections_json'] else []
        metrics = json.loads(r['image_metrics_json']) if r['image_metrics_json'] else {}
        results.append({
            'id': r['id'],
            'timestamp': r['timestamp'],
            'camera_id': r['camera_id'],
            'threat_level': r['threat_level'],
            'alert_level': r['threat_level'],
            'weapon_detected': bool(r['weapon_detected']),
            'weapon_class': r['weapon_class'],
            'confidence': r['confidence'],
            'status': r['status'],
            'notes': r['notes'],
            'detections': dets,
            'image_metrics': metrics
        })
    return results

def get_cctv_cameras():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cctv_cameras")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_audit(action, details=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_audit (timestamp, action, details)
        VALUES (?, ?, ?)
    """, (datetime.now(timezone.utc).isoformat(), action, details))
    conn.commit()
    conn.close()

def get_audit_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_audit ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_threat_definitions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threat_definitions")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_incident_status(incident_id, status, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    if notes:
        cursor.execute("UPDATE incidents SET status = ?, notes = ? WHERE id = ?", (status, notes, incident_id))
    else:
        cursor.execute("UPDATE incidents SET status = ? WHERE id = ?", (status, incident_id))
    conn.commit()
    conn.close()
