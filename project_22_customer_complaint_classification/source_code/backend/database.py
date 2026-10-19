"""
Relational SQLite Database Layer for PROJECT-022:
Customer Complaint Classification and Priority Routing Engine.

Schema:
- complaints: Full ticket lifecycle with NLP predictions, routing, and resolution status
- departments: Operational engineering & support departments with SLA quotas
- sla_policies: SLA targets, escalation triggers, and badge styling
- system_audit: Complete tamper-evident transactional audit log
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta, timezone
import random

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "complaints.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        code TEXT NOT NULL,
        lead_engineer TEXT NOT NULL,
        queue_capacity INTEGER NOT NULL,
        sla_target_hours REAL NOT NULL,
        active_tickets INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sla_policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        priority TEXT UNIQUE NOT NULL,
        sla_hours REAL NOT NULL,
        escalation_hours REAL NOT NULL,
        badge_color TEXT NOT NULL,
        notification_channel TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        complaint TEXT NOT NULL,
        category TEXT NOT NULL,
        category_label TEXT NOT NULL,
        category_icon TEXT NOT NULL,
        department TEXT NOT NULL,
        priority TEXT NOT NULL,
        priority_label TEXT NOT NULL,
        confidence REAL NOT NULL,
        probabilities_json TEXT NOT NULL,
        urgency_score INTEGER NOT NULL,
        sentiment_score REAL NOT NULL,
        sla_hours REAL NOT NULL,
        sla_deadline TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        notes TEXT DEFAULT '',
        matched_keywords TEXT DEFAULT '',
        summary TEXT NOT NULL
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

    # Seed departments if empty
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        departments_data = [
            ("FinOps Billing & Fraud Team", "FIN-OPS", "Elena Rostova", 150, 2.0),
            ("Quality Engineering & RMA Desk", "QA-RMA", "Marcus Vance", 100, 4.0),
            ("Global Supply Chain & Logistics", "LOG-OPS", "Devon Patel", 200, 8.0),
            ("Tier-3 Engineering & DevOps", "ENG-DEV", "Sarah Jenkins", 80, 1.0),
            ("Identity & Access Management (IAM)", "SEC-IAM", "Alexander Wu", 120, 2.0),
            ("Executive Customer Relations", "EXEC-REL", "Camilla Thorne", 60, 4.0)
        ]
        cursor.executemany("""
            INSERT INTO departments (name, code, lead_engineer, queue_capacity, sla_target_hours)
            VALUES (?, ?, ?, ?, ?)
        """, departments_data)
        conn.commit()

    # Seed SLA policies if empty
    cursor.execute("SELECT COUNT(*) FROM sla_policies")
    if cursor.fetchone()[0] == 0:
        sla_data = [
            ("critical", 0.5, 0.25, "#ef4444", "PagerDuty Executive On-Call"),
            ("high", 2.0, 1.0, "#f97316", "Slack #ops-escalation"),
            ("medium", 8.0, 4.0, "#eab308", "Jira Service Desk Tier-2"),
            ("low", 24.0, 12.0, "#10b981", "Email General Support Queue")
        ]
        cursor.executemany("""
            INSERT INTO sla_policies (priority, sla_hours, escalation_hours, badge_color, notification_channel)
            VALUES (?, ?, ?, ?, ?)
        """, sla_data)
        conn.commit()

    # Seed historical complaints if empty
    cursor.execute("SELECT COUNT(*) FROM complaints")
    if cursor.fetchone()[0] == 0:
        seed_historical_tickets(conn)

    conn.close()

def seed_historical_tickets(conn):
    cursor = conn.cursor()
    historical_samples = [
        (
            "My corporate card was charged $1,490 twice for order #88492. I need an immediate reversal and refund! This is an unauthorized charge.",
            "payment_issue", "Payment & Billing Dispute", "💳", "FinOps Billing & Fraud Team",
            "critical", "CRITICAL", 0.982,
            {"payment_issue": 0.982, "account_issue": 0.010, "service_dissatisfaction": 0.005, "technical_issue": 0.002, "delivery_problem": 0.001, "product_complaint": 0.000},
            94, -0.85, 0.5, "RESOLVED", "Refund settled via Stripe payment gateway batch #88492-R",
            "charge, refund, billing, unauthorized"
        ),
        (
            "The industrial laser printer motor stopped turning after 2 days. The spindle is cracked and burning plastic smell is coming out. RMA needed.",
            "product_complaint", "Product Defect & Hardware RMA", "📦", "Quality Engineering & RMA Desk",
            "high", "HIGH", 0.965,
            {"product_complaint": 0.965, "technical_issue": 0.020, "service_dissatisfaction": 0.010, "delivery_problem": 0.003, "payment_issue": 0.001, "account_issue": 0.001},
            82, -0.72, 2.0, "IN_PROGRESS", "Replacement spindle dispatched via DHL Express RMA-00219",
            "spindle, cracked, motor, burning, rma"
        ),
        (
            "Air cargo tracking #ORB-99120 has been stuck in Frankfurt transit for 9 days. Our assembly line is blocked waiting for these microchips.",
            "delivery_problem", "Logistics & Dispatch Delay", "🚚", "Global Supply Chain & Logistics",
            "high", "HIGH", 0.954,
            {"delivery_problem": 0.954, "service_dissatisfaction": 0.030, "product_complaint": 0.010, "technical_issue": 0.004, "payment_issue": 0.001, "account_issue": 0.001},
            78, -0.65, 2.0, "ASSIGNED", "Customs broker assigned to expedite cleared entry",
            "tracking, stuck, transit, delivery"
        ),
        (
            "Production API endpoint /v2/telemetry returning HTTP 500 internal server error during high load peaks. Affecting 40k connected sensors.",
            "technical_issue", "Software Bug & Platform Outage", "💻", "Tier-3 Engineering & DevOps",
            "critical", "CRITICAL", 0.991,
            {"technical_issue": 0.991, "account_issue": 0.005, "service_dissatisfaction": 0.002, "payment_issue": 0.001, "delivery_problem": 0.001, "product_complaint": 0.000},
            98, -0.92, 0.5, "RESOLVED", "Autoscaling group min replicas increased to 16, bug patched in v2.4.1",
            "api, 500, error, server, timeout"
        ),
        (
            "Our team lead is locked out of the enterprise console after MFA reset. Cannot access billing or user administration.",
            "account_issue", "IAM & Account Security", "🔐", "Identity & Access Management (IAM)",
            "medium", "MEDIUM", 0.941,
            {"account_issue": 0.941, "payment_issue": 0.030, "service_dissatisfaction": 0.015, "technical_issue": 0.010, "delivery_problem": 0.002, "product_complaint": 0.002},
            55, -0.38, 8.0, "RESOLVED", "Identity verified via hardware YubiKey challenge and access restored",
            "locked, mfa, account, access"
        ),
        (
            "Your Tier-1 support representative closed my support ticket without resolving the bug or providing any explanation. Completely unacceptable.",
            "service_dissatisfaction", "Customer Experience & SLA Escalation", "🤝", "Executive Customer Relations",
            "medium", "MEDIUM", 0.925,
            {"service_dissatisfaction": 0.925, "technical_issue": 0.040, "account_issue": 0.015, "payment_issue": 0.010, "delivery_problem": 0.005, "product_complaint": 0.005},
            60, -0.48, 8.0, "IN_PROGRESS", "Assigned to Senior Escalations Manager for customer call",
            "support, ticket, closed, rude, service"
        ),
        (
            "Received shipment box with water damage. 4 out of 10 lithium batteries arrived crushed and leaking electrolyte.",
            "product_complaint", "Product Defect & Hardware RMA", "📦", "Quality Engineering & RMA Desk",
            "critical", "CRITICAL", 0.978,
            {"product_complaint": 0.978, "delivery_problem": 0.015, "service_dissatisfaction": 0.005, "technical_issue": 0.001, "payment_issue": 0.001, "account_issue": 0.000},
            92, -0.88, 0.5, "ASSIGNED", "Hazardous materials response logged; full replacement dispatched",
            "damaged, crushed, leaking, product, defective"
        ),
        (
            "Requesting an official invoice receipt breakdown for our tax filing next month.",
            "payment_issue", "Payment & Billing Dispute", "💳", "FinOps Billing & Fraud Team",
            "low", "LOW", 0.912,
            {"payment_issue": 0.912, "account_issue": 0.050, "service_dissatisfaction": 0.020, "technical_issue": 0.010, "delivery_problem": 0.005, "product_complaint": 0.003},
            22, 0.05, 24.0, "RESOLVED", "PDF tax invoice receipt sent to customer controller",
            "invoice, receipt, tax, billing"
        )
    ]

    now = datetime.now(timezone.utc)
    for item in historical_samples:
        (text, cat, cat_label, icon, dept, prio, prio_label, conf, probs, urg, sent, sla_h, status, notes, kws) = item
        past_minutes = random.randint(15, 720)
        t_time = (now - timedelta(minutes=past_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        deadline = (now - timedelta(minutes=past_minutes) + timedelta(hours=sla_h)).strftime("%Y-%m-%d %H:%M UTC")
        summary = f"Customer flagged {cat_label.lower()} needing routing to {dept} with {prio_label} priority."

        cursor.execute("""
            INSERT INTO complaints (
                timestamp, complaint, category, category_label, category_icon, department,
                priority, priority_label, confidence, probabilities_json, urgency_score,
                sentiment_score, sla_hours, sla_deadline, status, notes, matched_keywords, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t_time, text, cat, cat_label, icon, dept, prio, prio_label, conf,
            json.dumps(probs), urg, sent, sla_h, deadline, status, notes, kws, summary
        ))

        cursor.execute("""
            INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
            VALUES (?, ?, ?, ?, ?)
        """, (
            t_time, "HISTORICAL_INGESTION", f"Ticket seeded for {cat_label} (Priority: {prio_label})", "127.0.0.1", "SUCCESS"
        ))

    conn.commit()

def add_complaint(complaint_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (
            timestamp, complaint, category, category_label, category_icon, department,
            priority, priority_label, confidence, probabilities_json, urgency_score,
            sentiment_score, sla_hours, sla_deadline, status, notes, matched_keywords, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_data['timestamp'],
        complaint_data['complaint'],
        complaint_data['category'],
        complaint_data['category_label'],
        complaint_data['category_icon'],
        complaint_data['department'],
        complaint_data['priority'],
        complaint_data['priority_label'],
        complaint_data['confidence'],
        json.dumps(complaint_data['probabilities']),
        complaint_data['urgency_score'],
        complaint_data['sentiment_score'],
        complaint_data['sla_hours'],
        complaint_data['sla_deadline'],
        complaint_data.get('status', 'PENDING'),
        complaint_data.get('notes', ''),
        ", ".join(complaint_data.get('matched_keywords', [])),
        complaint_data['summary']
    ))
    ticket_id = cursor.lastrowid

    # Update active tickets count in department
    cursor.execute("""
        UPDATE departments 
        SET active_tickets = active_tickets + 1 
        WHERE name = ?
    """, (complaint_data['department'],))

    # Audit log
    cursor.execute("""
        INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (
        complaint_data['timestamp'],
        "TICKET_CLASSIFIED",
        f"Complaint #{ticket_id} routed to {complaint_data['department']} (Conf: {complaint_data['confidence']*100:.1f}%)",
        complaint_data.get('user_ip', '127.0.0.1'),
        "SUCCESS"
    ))

    conn.commit()
    conn.close()
    return ticket_id

def get_complaints(limit=50, category=None, priority=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if category and category != 'ALL':
        query += " AND category = ?"
        params.append(category)
    if priority and priority != 'ALL':
        query += " AND priority = ?"
        params.append(priority)
    if status and status != 'ALL':
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        if item.get('probabilities_json'):
            try:
                item['probabilities'] = json.loads(item['probabilities_json'])
            except Exception:
                item['probabilities'] = {}
        if item.get('matched_keywords'):
            item['matched_keywords'] = [k.strip() for k in item['matched_keywords'].split(',') if k.strip()]
        else:
            item['matched_keywords'] = []
        result.append(item)
    return result

def get_complaint_by_id(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        if item.get('probabilities_json'):
            item['probabilities'] = json.loads(item['probabilities_json'])
        return item
    return None

def update_ticket_status(ticket_id, new_status, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints
        SET status = ?, notes = CASE WHEN ? != '' THEN ? ELSE notes END
        WHERE id = ?
    """, (new_status, notes, notes, ticket_id))
    
    cursor.execute("""
        INSERT INTO system_audit (timestamp, event_type, details, user_ip, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "STATUS_UPDATED",
        f"Ticket #{ticket_id} updated to {new_status}. Notes: {notes}",
        "127.0.0.1",
        "SUCCESS"
    ))
    conn.commit()
    conn.close()
    return True

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    by_cat = {}
    cursor.execute("SELECT category, COUNT(*) FROM complaints GROUP BY category")
    for r in cursor.fetchall():
        by_cat[r[0]] = r[1]

    by_prio = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    cursor.execute("SELECT priority, COUNT(*) FROM complaints GROUP BY priority")
    for r in cursor.fetchall():
        by_prio[r[0]] = r[1]

    cursor.execute("SELECT AVG(urgency_score), AVG(confidence) FROM complaints")
    row = cursor.fetchone()
    avg_urgency = round(row[0] or 0.0, 1)
    avg_confidence = round((row[1] or 0.0) * 100, 1)

    by_status = {}
    cursor.execute("SELECT status, COUNT(*) FROM complaints GROUP BY status")
    for r in cursor.fetchall():
        by_status[r[0]] = r[1]

    conn.close()

    return {
        'total': total,
        'by_category': by_cat,
        'by_priority': by_prio,
        'by_status': by_status,
        'avg_urgency': avg_urgency,
        'avg_confidence_pct': avg_confidence
    }

def get_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_audit_logs(limit=25):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_audit ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
    stats = get_stats()
    print("Seeded statistics:", stats)
