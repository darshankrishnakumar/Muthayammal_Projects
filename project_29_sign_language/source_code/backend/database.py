"""
Real-Time Sign Language Translation & Speech Synthesis
Relational SQLite Database Layer with ACID Persistence & WAL Mode
"""

import os
import sqlite3
import json
from datetime import datetime, timezone, timedelta
import random

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "sign_language.db"))

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
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sign TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        speech_prompt TEXT NOT NULL,
        kinematic_rules TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS landmark_prototypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sign TEXT NOT NULL,
        landmark_json TEXT NOT NULL,
        flat_vector_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sign) REFERENCES vocabulary(sign) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS translation_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_uuid TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        sign TEXT NOT NULL,
        category TEXT NOT NULL,
        confidence REAL NOT NULL,
        confidence_pct REAL NOT NULL,
        handedness TEXT NOT NULL,
        latency_ms INTEGER NOT NULL,
        landmarks_json TEXT NOT NULL,
        top_candidates_json TEXT NOT NULL,
        speech_text TEXT NOT NULL,
        FOREIGN KEY (sign) REFERENCES vocabulary(sign)
    );

    CREATE TABLE IF NOT EXISTS speech_synthesis_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        spoken_text TEXT NOT NULL,
        voice_profile TEXT,
        rate REAL,
        pitch REAL,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_trans_timestamp ON translation_sessions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_trans_sign ON translation_sessions(sign);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """)

    conn.commit()
    conn.close()

def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Check if vocabulary already populated
    cursor.execute("SELECT COUNT(*) as cnt FROM vocabulary")
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        return

    # 38 ASL/ISL Signs
    dictionary_meta = {
        'HELLO': {'category': 'Greeting', 'description': 'Open palm waving forward from temple', 'icon': '👋', 'speech': 'Hello'},
        'THANK YOU': {'category': 'Courtesy', 'description': 'Flat hand moving forward from chin', 'icon': '🙏', 'speech': 'Thank you'},
        'PLEASE': {'category': 'Courtesy', 'description': 'Circular palm rub against chest', 'icon': '🤲', 'speech': 'Please'},
        'YES': {'category': 'Response', 'description': 'Closed fist nodding up and down', 'icon': '👍', 'speech': 'Yes'},
        'NO': {'category': 'Response', 'description': 'Index and middle finger tapping thumb', 'icon': '👎', 'speech': 'No'},
        'HELP': {'category': 'Emergency', 'description': 'Closed fist with thumb up resting on open palm lifting', 'icon': '🆘', 'speech': 'Help needed'},
        'I LOVE YOU': {'category': 'Expression', 'description': 'Thumb, index, and pinky extended simultaneously', 'icon': '🤟', 'speech': 'I love you'},
        'WATER': {'category': 'Need', 'description': 'W-handshape tapping chin twice', 'icon': '💧', 'speech': 'Water please'},
        'DOCTOR': {'category': 'Medical', 'description': 'Tapping wrist artery with bent index and middle fingers', 'icon': '🩺', 'speech': 'Call a doctor'},
        'EMERGENCY': {'category': 'Emergency', 'description': 'Shaking E-handshape with high urgency', 'icon': '🚨', 'speech': 'Emergency'},
        'GOOD': {'category': 'Adjective', 'description': 'Flat hand moving forward from mouth into resting palm', 'icon': '✨', 'speech': 'Good'},
        'WELCOME': {'category': 'Greeting', 'description': 'Open arm sweeping gently toward body', 'icon': '🤝', 'speech': 'You are welcome'}
    }
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        dictionary_meta[ch] = {
            'category': 'Alphabet',
            'description': f'Fingerspelling letter {ch}',
            'icon': '🔤',
            'speech': ch
        }

    for sign, info in dictionary_meta.items():
        cursor.execute("""
            INSERT INTO vocabulary (sign, category, description, icon, speech_prompt, kinematic_rules)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sign,
            info['category'],
            info['description'],
            info['icon'],
            info['speech'],
            json.dumps({'sign': sign, 'category': info['category']})
        ))

    # Audit initialization
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity)
        VALUES (?, 'SYSTEM_INIT', 'Relational database schema initialized with WAL mode and 38 vocabulary tokens.', 'INFO')
    """, (now_iso,))

    conn.commit()
    conn.close()

def log_translation(session_uuid, sign_data):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO translation_sessions
        (session_uuid, timestamp, sign, category, confidence, confidence_pct, handedness, latency_ms, landmarks_json, top_candidates_json, speech_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_uuid,
        now_iso,
        sign_data['sign'],
        sign_data.get('category', 'General'),
        sign_data['confidence'],
        sign_data['confidence_pct'],
        sign_data.get('handedness', 'Right'),
        sign_data.get('latency_ms', 24),
        json.dumps(sign_data.get('landmarks_21', [])),
        json.dumps(sign_data.get('top_candidates', [])),
        sign_data.get('speech_text', sign_data['sign'])
    ))

    # Insert audit entry
    cursor.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity)
        VALUES (?, 'SIGN_RECOGNIZED', ?, 'INFO')
    """, (now_iso, f"Recognized sign '{sign_data['sign']}' with confidence {sign_data['confidence_pct']}%."))

    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def log_speech(spoken_text, voice="en-US", rate=1.0, pitch=1.0, status="COMPLETED"):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO speech_synthesis_logs (timestamp, spoken_text, voice_profile, rate, pitch, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (now_iso, spoken_text, voice, rate, pitch, status))

    conn.commit()
    conn.close()

def get_recent_translations(limit=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ts.*, v.icon, v.description
        FROM translation_sessions ts
        LEFT JOIN vocabulary v ON ts.sign = v.sign
        ORDER BY ts.timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            'id': r['id'],
            'session_uuid': r['session_uuid'],
            'timestamp': r['timestamp'],
            'sign': r['sign'],
            'category': r['category'],
            'description': r['description'] or '',
            'icon': r['icon'] or '✋',
            'confidence': r['confidence'],
            'confidence_pct': r['confidence_pct'],
            'handedness': r['handedness'],
            'latency_ms': r['latency_ms'],
            'landmarks_21': json.loads(r['landmarks_json']),
            'top_candidates': json.loads(r['top_candidates_json']),
            'speech_text': r['speech_text']
        })
    conn.close()
    return results

def get_all_vocabulary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vocabulary ORDER BY id ASC")
    rows = cursor.fetchall()
    vocab = {}
    for r in rows:
        vocab[r['sign']] = {
            'category': r['category'],
            'description': r['description'],
            'icon': r['icon'],
            'speech_prompt': r['speech_prompt']
        }
    conn.close()
    return vocab

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
    cursor.execute("SELECT COUNT(*) FROM translation_sessions;")
    sessions_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM vocabulary;")
    vocab_count = cursor.fetchone()[0]
    conn.close()
    return {
        'journal_mode': mode.upper(),
        'wal_enabled': mode.upper() == 'WAL',
        'translation_sessions_count': sessions_count,
        'vocabulary_count': vocab_count
    }

if __name__ == '__main__':
    seed_database()
    print("Database seeded and verified:")
    print(verify_wal_status())
