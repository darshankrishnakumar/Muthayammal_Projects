"""
Relational SQLite Database Layer for PROJECT-023:
AI Meeting Summarization & Action-Item Extraction Engine.

Schema:
- meetings: Meeting metadata, executive summaries, duration, metrics
- action_items: Individual assigned tasks with priority, deadline, status
- decisions: Strategic consensus agreements and architectural decisions
- system_audit: Transactional compliance audit log
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "meetings.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        transcript TEXT NOT NULL,
        executive_summary TEXT NOT NULL,
        summary_bullets_json TEXT NOT NULL,
        word_count INTEGER NOT NULL,
        duration_est_mins REAL NOT NULL,
        compression_ratio_pct REAL NOT NULL,
        sentiment_index REAL NOT NULL,
        engagement_score REAL NOT NULL,
        speaker_stats_json TEXT NOT NULL,
        status TEXT DEFAULT 'PROCESSED'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS action_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        assignee TEXT NOT NULL,
        priority TEXT NOT NULL,
        category TEXT NOT NULL,
        deadline TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER NOT NULL,
        decision_text TEXT NOT NULL,
        FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        user_ip TEXT NOT NULL,
        outcome TEXT NOT NULL
    );
    """)

    conn.commit()

    # Seed historical sessions if empty
    cursor.execute("SELECT COUNT(*) FROM meetings")
    if cursor.fetchone()[0] == 0:
        seed_historical_meetings(conn)

    conn.close()

def seed_historical_meetings(conn):
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    meetings = [
        {
            "title": "Q3 Cloud Architecture & Security Review",
            "timestamp": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": """[Sarah (Product Lead)]: Good morning everyone. Let's review the Q3 Cloud Architecture and latency benchmarks.
[Marcus (Chief Architect)]: Thanks Sarah. The migration to Kafka streaming dropped our peak event processing latency from 420ms to 48ms. We decided to approve Kafka as our standard messaging backbone.
[Elena (DevOps SRE)]: On the infra side, I will deploy the canary release v2.4 to the staging Kubernetes cluster by Friday. We must ensure memory limits are tuned.
[David (Engineering Mgr)]: Great. I will sync with Finance on cloud infrastructure budget allocation by Monday. We agreed on keeping the European failover region hot.
[Priya (Data Lead)]: I need to train the fine-tuned embedding model on our internal technical documentation by next sprint to boost RAG search recall.
[Sarah (Product Lead)]: Excellent progress team. All action items are approved and tracked.""",
            "executive_summary": "The architecture committee reviewed Q3 telemetry improvements resulting from the Apache Kafka migration. Key deployment safeguards were established for canary release v2.4, European hot failover was confirmed, and model fine-tuning was scheduled to improve technical retrieval recall.",
            "summary_bullets": [
                "Kafka messaging backbone approved as primary event streaming standard (peak latency down from 420ms to 48ms).",
                "Canary v2.4 deployment scheduled for staging cluster with memory limit verifications by Friday.",
                "European secondary failover region maintained in hot state for enterprise high-availability.",
                "RAG fine-tuned embedding model training committed for next sprint delivery."
            ],
            "word_count": 142,
            "duration_est_mins": 8.5,
            "compression_ratio_pct": 32.4,
            "sentiment_index": 0.82,
            "engagement_score": 91.5,
            "speaker_stats": {
                "Sarah (Product Lead)": 35,
                "Marcus (Chief Architect)": 38,
                "Elena (DevOps SRE)": 32,
                "David (Engineering Mgr)": 34,
                "Priya (Data Lead)": 26
            },
            "actions": [
                ("Deploy canary release v2.4 to staging cluster with memory limits", "Elena (DevOps SRE)", "High", "DevOps", "Friday 5 PM"),
                ("Sync with Finance on cloud infrastructure budget allocation", "David (Engineering Mgr)", "Medium", "Management", "Monday EOD"),
                ("Train fine-tuned embedding model on internal documentation", "Priya (Data Lead)", "High", "AI/ML", "Next Sprint")
            ],
            "decisions": [
                "Approved Kafka as primary streaming backbone across all core telemetry services.",
                "Agreed to keep the European regional failover cluster active in hot standby."
            ]
        },
        {
            "title": "Sprint 42 Planning & Customer Blocker Triage",
            "timestamp": (now - timedelta(hours=28)).strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": """[David (Engineering Mgr)]: Welcome to Sprint 42 planning. We have 3 primary customer blockers from the enterprise pilot.
[Marcus (Chief Architect)]: I will optimize the PostgreSQL index scan on the payments ledger table by tomorrow morning to fix the dashboard timeout.
[Elena (DevOps SRE)]: We decided to automate zero-downtime certificate renewals using Let's Encrypt bot on our edge gateways.
[Sarah (Product Lead)]: I will review the API deprecation schedule with the enterprise partners before Wednesday.
[Priya (Data Lead)]: I will benchmark the vector embedding retrieval latency and publish the test suite results by end of week.""",
            "executive_summary": "Sprint 42 planning prioritized 3 enterprise pilot blockers. Engineering leads committed to database query optimizations for billing dashboards, automated edge certificate provisioning, and vector database latency benchmarking.",
            "summary_bullets": [
                "Prioritized 3 urgent customer blockers impacting enterprise pilot tenants.",
                "PostgreSQL index optimization committed for tomorrow to resolve dashboard timeouts.",
                "Zero-downtime edge gateway certificate renewal automated via Let's Encrypt.",
                "Vector retrieval latency benchmark suite scheduled for end-of-week release."
            ],
            "word_count": 128,
            "duration_est_mins": 7.2,
            "compression_ratio_pct": 29.8,
            "sentiment_index": 0.76,
            "engagement_score": 88.0,
            "speaker_stats": {
                "David (Engineering Mgr)": 28,
                "Marcus (Chief Architect)": 26,
                "Elena (DevOps SRE)": 24,
                "Sarah (Product Lead)": 22,
                "Priya (Data Lead)": 24
            },
            "actions": [
                ("Optimize PostgreSQL index scan on payments ledger table", "Marcus (Chief Architect)", "Critical", "Architecture", "Tomorrow 10 AM"),
                ("Automate edge certificate renewals via Let's Encrypt bot", "Elena (DevOps SRE)", "High", "Security", "Friday EOD"),
                ("Review API deprecation schedule with enterprise partners", "Sarah (Product Lead)", "Medium", "Product", "Wednesday 2 PM"),
                ("Benchmark vector embedding retrieval latency test suite", "Priya (Data Lead)", "High", "Data/AI", "End of Week")
            ],
            "decisions": [
                "Approved automated zero-downtime certificate renewals on all ingress gateways.",
                "Agreed to hold non-blocking feature development until database timeouts are resolved."
            ]
        }
    ]

    for m in meetings:
        cursor.execute("""
            INSERT INTO meetings (
                title, timestamp, transcript, executive_summary, summary_bullets_json,
                word_count, duration_est_mins, compression_ratio_pct, sentiment_index,
                engagement_score, speaker_stats_json, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m['title'], m['timestamp'], m['transcript'], m['executive_summary'],
            json.dumps(m['summary_bullets']), m['word_count'], m['duration_est_mins'],
            m['compression_ratio_pct'], m['sentiment_index'], m['engagement_score'],
            json.dumps(m['speaker_stats']), "PROCESSED"
        ))
        meeting_id = cursor.lastrowid

        for task, who, prio, cat, due in m['actions']:
            cursor.execute("""
                INSERT INTO action_items (meeting_id, task, assignee, priority, category, deadline, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (meeting_id, task, who, prio, cat, due, "OPEN"))

        for dec in m['decisions']:
            cursor.execute("""
                INSERT INTO decisions (meeting_id, decision_text)
                VALUES (?, ?)
            """, (meeting_id, dec))

        cursor.execute("""
            INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
            VALUES (?, ?, ?, ?, ?)
        """, (
            m['timestamp'], "HISTORICAL_INGESTION", f"Meeting seeded: {m['title']} (#{meeting_id})", "127.0.0.1", "SUCCESS"
        ))

    conn.commit()

def add_meeting(meeting_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO meetings (
            title, timestamp, transcript, executive_summary, summary_bullets_json,
            word_count, duration_est_mins, compression_ratio_pct, sentiment_index,
            engagement_score, speaker_stats_json, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meeting_data['title'],
        meeting_data['timestamp'],
        meeting_data['transcript'],
        meeting_data['executive_summary'],
        json.dumps(meeting_data['summary_bullets']),
        meeting_data['word_count'],
        meeting_data['duration_est_mins'],
        meeting_data['compression_ratio_pct'],
        meeting_data['sentiment_index'],
        meeting_data['engagement_score'],
        json.dumps(meeting_data['speaker_stats']),
        meeting_data.get('status', 'PROCESSED')
    ))
    meeting_id = cursor.lastrowid

    for item in meeting_data.get('action_items', []):
        cursor.execute("""
            INSERT INTO action_items (meeting_id, task, assignee, priority, category, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            meeting_id,
            item['task'],
            item['assignee'],
            item['priority'],
            item.get('category', 'General'),
            item.get('deadline', 'End of Week'),
            item.get('status', 'OPEN')
        ))

    for dec in meeting_data.get('decisions', []):
        cursor.execute("""
            INSERT INTO decisions (meeting_id, decision_text)
            VALUES (?, ?)
        """, (meeting_id, dec))

    cursor.execute("""
        INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (
        meeting_data['timestamp'],
        "MEETING_SUMMARIZED",
        f"Meeting #{meeting_id} '{meeting_data['title']}' summarized with {len(meeting_data.get('action_items', []))} action items",
        meeting_data.get('user_ip', '127.0.0.1'),
        "SUCCESS"
    ))

    conn.commit()
    conn.close()
    return meeting_id

def get_meetings(limit=25):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        item = dict(r)
        if item.get('summary_bullets_json'):
            item['summary_bullets'] = json.loads(item['summary_bullets_json'])
        if item.get('speaker_stats_json'):
            item['speaker_stats'] = json.loads(item['speaker_stats_json'])

        # Fetch action items
        cursor.execute("SELECT * FROM action_items WHERE meeting_id = ?", (item['id'],))
        item['action_items'] = [dict(a) for a in cursor.fetchall()]

        # Fetch decisions
        cursor.execute("SELECT decision_text FROM decisions WHERE meeting_id = ?", (item['id'],))
        item['decisions'] = [d[0] for d in cursor.fetchall()]

        result.append(item)

    conn.close()
    return result

def get_meeting_by_id(meeting_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    item = dict(row)
    if item.get('summary_bullets_json'):
        item['summary_bullets'] = json.loads(item['summary_bullets_json'])
    if item.get('speaker_stats_json'):
        item['speaker_stats'] = json.loads(item['speaker_stats_json'])

    cursor.execute("SELECT * FROM action_items WHERE meeting_id = ?", (meeting_id,))
    item['action_items'] = [dict(a) for a in cursor.fetchall()]

    cursor.execute("SELECT decision_text FROM decisions WHERE meeting_id = ?", (meeting_id,))
    item['decisions'] = [d[0] for d in cursor.fetchall()]

    conn.close()
    return item

def update_action_status(action_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE action_items SET status = ? WHERE id = ?", (new_status, action_id))
    cursor.execute("""
        INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "ACTION_STATUS_UPDATED",
        f"Action item #{action_id} changed to {new_status}",
        "127.0.0.1",
        "SUCCESS"
    ))
    conn.commit()
    conn.close()
    return True

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM meetings")
    total_meetings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM action_items")
    total_actions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM decisions")
    total_decisions = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(engagement_score) FROM meetings")
    avg_eng = cursor.fetchone()[0] or 88.0

    conn.close()
    return {
        'total_meetings': total_meetings,
        'total_action_items': total_actions,
        'total_decisions_logged': total_decisions,
        'avg_engagement_pct': round(avg_eng, 1)
    }

def get_audit_logs(limit=25):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_audit ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == '__main__':
    init_db()
    print("Meetings DB initialized at:", DB_PATH)
    print("Initial stats:", get_stats())
