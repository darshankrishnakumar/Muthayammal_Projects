import os
import sqlite3
import json
import random
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speech_emotion.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audio_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL,
        duration_seconds REAL NOT NULL,
        note TEXT,
        emotion TEXT NOT NULL,
        emotion_label TEXT NOT NULL,
        emotion_icon TEXT NOT NULL,
        color TEXT NOT NULL,
        confidence REAL NOT NULL,
        confidence_pct REAL NOT NULL,
        valence REAL NOT NULL,
        arousal REAL NOT NULL,
        pitch_f0_hz REAL NOT NULL,
        rms_energy_db REAL NOT NULL,
        spectral_centroid_hz REAL NOT NULL,
        zero_crossing_rate REAL NOT NULL,
        spectral_rolloff_hz REAL NOT NULL,
        jitter_local_pct REAL NOT NULL,
        shimmer_local_pct REAL NOT NULL,
        mfcc_coefficients_json TEXT NOT NULL,
        emotion_distribution_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emotion_benchmarks (
        emotion TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        icon TEXT NOT NULL,
        color TEXT NOT NULL,
        valence REAL NOT NULL,
        arousal REAL NOT NULL,
        sample_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_stats (
        lang_code TEXT PRIMARY KEY,
        lang_name TEXT NOT NULL,
        flag TEXT NOT NULL,
        total_analyzed INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM emotion_benchmarks")
    if cursor.fetchone()[0] == 0:
        seed_benchmarks(conn)

    cursor.execute("SELECT COUNT(*) FROM language_stats")
    if cursor.fetchone()[0] == 0:
        seed_languages(conn)

    cursor.execute("SELECT COUNT(*) FROM audio_sessions")
    if cursor.fetchone()[0] == 0:
        seed_sessions(conn)

    conn.close()

def seed_benchmarks(conn):
    cursor = conn.cursor()
    benchmarks = [
        ('happy', 'Joy & Happiness', '😊', '#10b981', 0.78, 0.62),
        ('sad', 'Sadness & Dejection', '😢', '#3b82f6', -0.72, -0.55),
        ('angry', 'Anger & Frustration', '😡', '#ef4444', -0.81, 0.88),
        ('fear', 'Fear & Anxiety', '😨', '#8b5cf6', -0.65, 0.74),
        ('neutral', 'Calm & Neutral', '😐', '#94a3b8', 0.05, 0.02),
        ('surprise', 'Surprise & Wonder', '😲', '#f59e0b', 0.45, 0.79),
        ('disgust', 'Disgust & Contempt', '🤢', '#ec4899', -0.76, 0.42)
    ]
    for b in benchmarks:
        cursor.execute("""
        INSERT OR REPLACE INTO emotion_benchmarks (emotion, label, icon, color, valence, arousal, sample_count)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, b)
    conn.commit()

def seed_languages(conn):
    cursor = conn.cursor()
    langs = [
        ('en', 'English', '🇺🇸'),
        ('hi', 'Hindi', '🇮🇳'),
        ('ta', 'Tamil', '🇮🇳'),
        ('es', 'Spanish', '🇪🇸'),
        ('fr', 'French', '🇫🇷'),
        ('de', 'German', '🇩🇪'),
        ('zh', 'Mandarin', '🇨🇳'),
        ('ja', 'Japanese', '🇯🇵')
    ]
    for l in langs:
        cursor.execute("""
        INSERT OR REPLACE INTO language_stats (lang_code, lang_name, flag, total_analyzed)
        VALUES (?, ?, ?, 0)
        """, l)
    conn.commit()

def seed_sessions(conn):
    cursor = conn.cursor()
    seeds = [
        ('English', 4.2, 'Customer escalated billing timeout', 'angry', 'Anger & Frustration', '😡', '#ef4444', 0.942, 94.2, -0.82, 0.89, 265.0, 0.84, 2820.0, 0.18, 5650.0, 1.2, 3.5),
        ('Spanish', 3.5, '5-star positive service feedback', 'happy', 'Joy & Happiness', '😊', '#10b981', 0.961, 96.1, 0.79, 0.63, 242.0, 0.69, 2380.0, 0.14, 4790.0, 0.8, 2.3),
        ('Hindi', 5.0, 'Emergency telemedicine advisory call', 'fear', 'Fear & Anxiety', '😨', '#8b5cf6', 0.935, 93.5, -0.66, 0.75, 288.0, 0.73, 3120.0, 0.21, 6250.0, 1.8, 4.7),
        ('French', 2.8, 'Routine calendar scheduling confirmation', 'neutral', 'Calm & Neutral', '😐', '#94a3b8', 0.912, 91.2, 0.04, 0.01, 174.0, 0.44, 1740.0, 0.09, 3780.0, 0.5, 1.9),
        ('Tamil', 4.6, 'Hardware malfunction return inquiry', 'sad', 'Sadness & Dejection', '😢', '#3b82f6', 0.928, 92.8, -0.71, -0.54, 138.0, 0.27, 1490.0, 0.07, 3190.0, 1.6, 4.1),
        ('German', 3.2, 'Unexpected product upgrade announcement', 'surprise', 'Surprise & Wonder', '😲', '#f59e0b', 0.948, 94.8, 0.46, 0.80, 272.0, 0.76, 2610.0, 0.16, 5210.0, 1.0, 2.8),
        ('Mandarin', 3.8, 'Spoiled food shipment delivery complaint', 'disgust', 'Disgust & Contempt', '🤢', '#ec4899', 0.954, 95.4, -0.77, 0.43, 192.0, 0.56, 1910.0, 0.11, 4120.0, 1.4, 3.9),
        ('Japanese', 4.0, 'Executive team milestone celebration', 'happy', 'Joy & Happiness', '😊', '#10b981', 0.973, 97.3, 0.81, 0.65, 245.0, 0.71, 2410.0, 0.14, 4830.0, 0.7, 2.2)
    ]
    now = datetime.now(timezone.utc)
    for idx, s in enumerate(seeds):
        ts = (now - timedelta(minutes=random.randint(15, 300))).isoformat()
        mfccs = [round(float(random.uniform(-35, 35)), 2) for _ in range(13)]
        mfccs[0] = round(float(random.uniform(-260, -180)), 2)
        dist = {e: 0.01 for e in ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'disgust']}
        dist[s[3]] = s[7]
        rem = round(1.0 - s[7], 3)
        others = [e for e in dist if e != s[3]]
        for o in others:
            dist[o] = round(rem / len(others), 3)

        cursor.execute("""
        INSERT INTO audio_sessions 
        (language, duration_seconds, note, emotion, emotion_label, emotion_icon, color,
         confidence, confidence_pct, valence, arousal, pitch_f0_hz, rms_energy_db,
         spectral_centroid_hz, zero_crossing_rate, spectral_rolloff_hz, jitter_local_pct,
         shimmer_local_pct, mfcc_coefficients_json, emotion_distribution_json, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s[0], s[1], s[2], s[3], s[4], s[5], s[6],
            s[7], s[8], s[9], s[10], s[11], s[12],
            s[13], s[14], s[15], s[16], s[17],
            json.dumps(mfccs), json.dumps(dist), ts
        ))
        cursor.execute("UPDATE emotion_benchmarks SET sample_count = sample_count + 1 WHERE emotion = ?", (s[3],))

    cursor.execute("""
    INSERT INTO system_audit (event_type, details, timestamp)
    VALUES (?, ?, ?)
    """, ("DATABASE_INIT", "Speech emotion SQLite database initialized with benchmarks and seed sessions", now.isoformat()))
    conn.commit()

def save_audio_session(data):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()
    feats = data.get('features', {})

    cursor.execute("""
    INSERT INTO audio_sessions 
    (language, duration_seconds, note, emotion, emotion_label, emotion_icon, color,
     confidence, confidence_pct, valence, arousal, pitch_f0_hz, rms_energy_db,
     spectral_centroid_hz, zero_crossing_rate, spectral_rolloff_hz, jitter_local_pct,
     shimmer_local_pct, mfcc_coefficients_json, emotion_distribution_json, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('language', 'English'),
        float(data.get('duration_seconds', 3.0)),
        data.get('note', 'Live User Audio Stream'),
        data['emotion'],
        data['emotion_label'],
        data['emotion_icon'],
        data['color'],
        float(data['confidence']),
        float(data['confidence_pct']),
        float(data['valence']),
        float(data['arousal']),
        float(feats.get('pitch_f0_hz', 180.0)),
        float(feats.get('rms_energy_db', 0.5)),
        float(feats.get('spectral_centroid_hz', 2200.0)),
        float(feats.get('zero_crossing_rate', 0.12)),
        float(feats.get('spectral_rolloff_hz', 4500.0)),
        float(feats.get('jitter_local_pct', 1.0)),
        float(feats.get('shimmer_local_pct', 2.5)),
        json.dumps(feats.get('mfcc_coefficients', [])),
        json.dumps(data.get('emotion_distribution', {})),
        now_str
    ))
    session_id = cursor.lastrowid

    cursor.execute("UPDATE emotion_benchmarks SET sample_count = sample_count + 1 WHERE emotion = ?", (data['emotion'],))

    cursor.execute("""
    INSERT INTO system_audit (event_type, details, timestamp)
    VALUES (?, ?, ?)
    """, ("AUDIO_CLASSIFICATION", f"Classified session #{session_id} as {data['emotion']} ({data['confidence_pct']}%) in {data.get('language')}", now_str))

    conn.commit()
    conn.close()
    return session_id

def get_recent_sessions(limit=40):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audio_sessions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    sessions = []
    for r in rows:
        d = dict(r)
        d['features'] = {
            'pitch_f0_hz': d['pitch_f0_hz'],
            'rms_energy_db': d['rms_energy_db'],
            'spectral_centroid_hz': d['spectral_centroid_hz'],
            'zero_crossing_rate': d['zero_crossing_rate'],
            'spectral_rolloff_hz': d['spectral_rolloff_hz'],
            'jitter_local_pct': d['jitter_local_pct'],
            'shimmer_local_pct': d['shimmer_local_pct'],
            'mfcc_coefficients': json.loads(d['mfcc_coefficients_json']) if d['mfcc_coefficients_json'] else []
        }
        d['emotion_distribution'] = json.loads(d['emotion_distribution_json']) if d['emotion_distribution_json'] else {}
        sessions.append(d)
    conn.close()
    return sessions

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(confidence_pct) FROM audio_sessions")
    total, avg_conf = cursor.fetchone()
    total = total or 0
    avg_conf = round(avg_conf or 88.0, 1)

    cursor.execute("SELECT emotion, COUNT(*) FROM audio_sessions GROUP BY emotion")
    counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT * FROM emotion_benchmarks")
    benchmarks = {r['emotion']: dict(r) for r in cursor.fetchall()}

    conn.close()
    return {
        'total_samples': total,
        'avg_confidence_pct': avg_conf,
        'emotion_counts': counts,
        'supported_emotions': benchmarks
    }

def get_languages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lang_code as code, lang_name as name, flag, total_analyzed FROM language_stats")
    langs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return langs

def get_audit_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_audit ORDER BY id DESC LIMIT ?", (limit,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs
