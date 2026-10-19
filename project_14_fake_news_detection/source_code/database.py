import os
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_news.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                headline_preview TEXT NOT NULL,
                classification TEXT NOT NULL,
                confidence REAL NOT NULL,
                decision_score REAL NOT NULL,
                sensationalism_score REAL NOT NULL,
                speculative_score REAL NOT NULL,
                objective_score REAL NOT NULL,
                source_watermark_detected INTEGER NOT NULL,
                pure_language_mode INTEGER NOT NULL,
                full_text_hash TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_time ON news_verifications(timestamp)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_class ON news_verifications(classification)")
        conn.commit()

def log_verification(
    headline_preview: str,
    classification: str,
    confidence: float,
    decision_score: float,
    sensationalism_score: float,
    speculative_score: float,
    objective_score: float,
    source_watermark_detected: bool,
    pure_language_mode: bool,
    full_text_hash: str = ""
) -> int:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO news_verifications (
                timestamp, headline_preview, classification, confidence, decision_score,
                sensationalism_score, speculative_score, objective_score,
                source_watermark_detected, pure_language_mode, full_text_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str, headline_preview[:120], classification, round(float(confidence), 1),
            round(float(decision_score), 4), round(float(sensationalism_score), 1),
            round(float(speculative_score), 1), round(float(objective_score), 1),
            1 if source_watermark_detected else 0, 1 if pure_language_mode else 0, full_text_hash
        ))
        conn.commit()
        return cur.lastrowid

def get_recent_verifications(limit: int = 25) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, timestamp, headline_preview, classification, confidence,
                   decision_score, sensationalism_score, speculative_score, objective_score,
                   source_watermark_detected, pure_language_mode
            FROM news_verifications
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]

def get_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news_verifications")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM news_verifications WHERE classification LIKE '%REAL%'")
        real_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM news_verifications WHERE classification LIKE '%FAKE%'")
        fake_count = cur.fetchone()[0]

        cur.execute("SELECT AVG(confidence), AVG(sensationalism_score) FROM news_verifications")
        row = cur.fetchone()
        avg_conf = round(row[0], 1) if row[0] else 0.0
        avg_sens = round(row[1], 1) if row[1] else 0.0

        return {
            "total_verifications": total,
            "real_news_count": real_count,
            "fake_news_count": fake_count,
            "avg_confidence": avg_conf,
            "avg_sensationalism": avg_sens,
            "database_file": DB_FILE,
            "status": "connected"
        }

def seed_sample_records():
    init_db()
    stats = get_stats()
    if stats["total_verifications"] >= 20:
        return

    samples = [
        ("Federal Reserve issues formal monetary policy briefing on interest rate trajectory", "REAL", 94.2, 2.45, 2.0, 5.0, 88.0, 1, 0),
        ("SHOCKING BOMBSHELL: Secret classified documents expose hidden government mind control plot!", "FAKE", 96.8, -3.12, 92.0, 65.0, 4.0, 0, 1),
        ("Supreme Court delivers unanimous verdict regarding interstate commerce clause litigation", "REAL", 92.5, 2.10, 5.0, 10.0, 85.0, 1, 0),
        ("MIRACLE CURE: Doctors BANNED from revealing this one bizarre kitchen spice that dissolves fat", "FAKE", 98.4, -4.20, 95.0, 70.0, 2.0, 0, 1),
        ("European Space Agency schedules upcoming lunar rover mission for third quarter launch", "REAL", 89.6, 1.85, 3.0, 12.0, 80.0, 0, 0),
        ("UNBELIEVABLE PROOF: Leaked video confirms military base alien encounter coverup panic", "FAKE", 95.1, -2.85, 88.0, 80.0, 5.0, 0, 1),
        ("Ministry of Transportation signs bilateral aviation agreement expanding cargo capacity", "REAL", 91.0, 1.95, 4.0, 8.0, 82.0, 0, 0),
        ("URGENT ALERT: Mind-blowing conspiracy exposed as mainstream media enters furious meltdown", "FAKE", 97.2, -3.60, 94.0, 75.0, 3.0, 0, 1),
        ("National Weather Service issues coastal storm advisory ahead of Atlantic hurricane development", "REAL", 93.8, 2.30, 8.0, 15.0, 86.0, 1, 0),
        ("TERRIFYING NIGHTMARE: Banned scientists publish forbidden truth before being silenced forever", "FAKE", 98.9, -4.50, 96.0, 85.0, 1.0, 0, 1)
    ]

    base_time = datetime.now() - timedelta(days=4)
    for i, s in enumerate(samples * 2):  # 20 records
        t_str = (base_time + timedelta(hours=i*4, minutes=random.randint(2, 40))).strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO news_verifications (
                    timestamp, headline_preview, classification, confidence, decision_score,
                    sensationalism_score, speculative_score, objective_score,
                    source_watermark_detected, pure_language_mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t_str, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]
            ))
            conn.commit()

init_db()

if __name__ == "__main__":
    seed_sample_records()
    print("Database initialized and seeded:", get_stats())
