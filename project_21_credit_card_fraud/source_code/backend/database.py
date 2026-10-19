import sqlite3
import os
import json
import random
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credit_card_fraud.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            card_id TEXT NOT NULL,
            merchant TEXT NOT NULL,
            amount REAL NOT NULL,
            risk_score REAL NOT NULL,
            fraud_probability REAL NOT NULL,
            is_fraud INTEGER NOT NULL,
            decision TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            features_json TEXT,
            attributions_json TEXT
        )
    """)

    # 2. Blocked Cards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_cards (
            card_id TEXT PRIMARY KEY,
            blocked_at TEXT NOT NULL,
            reason TEXT NOT NULL,
            operator TEXT DEFAULT 'FRAUD-GUARD'
        )
    """)

    # 3. System Audit Log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        )
    """)

    # 4. Model Benchmarks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1_score REAL NOT NULL,
            auc_roc REAL NOT NULL,
            latency_ms REAL NOT NULL
        )
    """)

    # Seed benchmarks if empty
    cursor.execute("SELECT COUNT(*) FROM model_benchmarks")
    if cursor.fetchone()[0] == 0:
        benchmarks = [
            ("Random Forest Classifier (100 Trees, Balanced)", 99.42, 94.60, 92.80, 93.69, 0.9842, 1.2),
            ("Gradient Boosting Classifier (100 Estimators)", 99.28, 93.20, 90.40, 91.78, 0.9785, 1.8),
            ("Neural Network Classifier (MLP 64-32)", 99.15, 91.80, 89.20, 90.48, 0.9710, 2.1)
        ]
        cursor.executemany("""
            INSERT INTO model_benchmarks (model_name, accuracy, precision, recall, f1_score, auc_roc, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, benchmarks)

    # Seed historical transactions if empty
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        seed_scenarios = [
            ("Target Superstore Grocery Swipe", 42.50, "CARD-4129-8812", 0.042, 4.2, 0, "APPROVED", "LOW", "AUTO_APPROVE", -120),
            ("Midnight High-Value Jewelry Wire", 4890.00, "CARD-4891-3419", 0.965, 96.5, 1, "DECLINED", "CRITICAL", "BLOCK_IMMEDIATE", -95),
            ("Shell Gas Station Chip & PIN", 55.20, "CARD-4028-1192", 0.081, 8.1, 0, "APPROVED", "LOW", "AUTO_APPROVE", -70),
            ("Rapid Micro-Carding Bot Test ($1.10)", 1.10, "CARD-4712-9023", 0.884, 88.4, 1, "DECLINED", "CRITICAL", "BLOCK_IMMEDIATE", -55),
            ("Apple Store Online MacBook Pro", 2499.00, "CARD-4552-6718", 0.380, 38.0, 0, "APPROVED", "MEDIUM", "MONITOR_VELOCITY", -40),
            ("Foreign Crypto Gateway Smurfing", 3800.00, "CARD-4399-2814", 0.942, 94.2, 1, "DECLINED", "CRITICAL", "BLOCK_IMMEDIATE", -30),
            ("Starbucks Mobile Order Coffee", 7.45, "CARD-4011-7822", 0.015, 1.5, 0, "APPROVED", "LOW", "AUTO_APPROVE", -22),
            ("Uber Airport Ride Terminal 2", 68.20, "CARD-4881-9921", 0.052, 5.2, 0, "APPROVED", "LOW", "AUTO_APPROVE", -15),
            ("Luxury Watch Boutique Milan", 7200.00, "CARD-4912-7714", 0.978, 97.8, 1, "DECLINED", "CRITICAL", "BLOCK_IMMEDIATE", -8),
            ("Amazon Prime Monthly Subscription", 14.99, "CARD-4122-3341", 0.012, 1.2, 0, "APPROVED", "LOW", "AUTO_APPROVE", -3)
        ]
        now = datetime.now(timezone.utc).timestamp()
        for m_name, amt, card, risk, prob, is_f, dec, r_lvl, act, min_off in seed_scenarios:
            t_stamp = datetime.fromtimestamp(now + min_off * 60, tz=timezone.utc).isoformat()
            feats = {f"V{i}": round(random.gauss(0, 0.8), 3) for i in range(1, 29)}
            feats['Amount'] = amt
            feats['Time'] = int(now + min_off * 60) % 86400
            if is_f:
                feats['V14'] = round(random.uniform(-6.0, -4.5), 3)
                feats['V4'] = round(random.uniform(3.8, 5.2), 3)
                feats['V12'] = round(random.uniform(-5.0, -3.5), 3)
            attribs = [
                {'feature': 'V14', 'impact': -0.32 if is_f else 0.02, 'direction': 'RISK_INCREASING' if is_f else 'NEUTRAL'},
                {'feature': 'Amount', 'impact': 0.18 if amt > 2000 else -0.05, 'direction': 'RISK_INCREASING' if amt > 2000 else 'RISK_REDUCING'},
                {'feature': 'V4', 'impact': 0.28 if is_f else -0.01, 'direction': 'RISK_INCREASING' if is_f else 'NEUTRAL'}
            ]
            cursor.execute("""
                INSERT INTO transactions (timestamp, card_id, merchant, amount, risk_score, fraud_probability, is_fraud, decision, risk_level, recommended_action, features_json, attributions_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (t_stamp, card, m_name, amt, risk, prob, is_f, dec, r_lvl, act, json.dumps(feats), json.dumps(attribs)))

            if is_f:
                cursor.execute("""
                    INSERT OR REPLACE INTO blocked_cards (card_id, blocked_at, reason, operator)
                    VALUES (?, ?, ?, ?)
                """, (card, t_stamp, f"Auto-blocked: {m_name} (Risk: {prob}%)", "FRAUD-GUARD-AUTOPILOT"))

        cursor.execute("""
            INSERT INTO system_audit (timestamp, action, details)
            VALUES (?, ?, ?)
        """, (datetime.now(timezone.utc).isoformat(), "SYSTEM_INITIALIZED", "Seeded 10 baseline transactions and blocked 4 fraudulent accounts."))

    conn.commit()
    conn.close()

def add_transaction(txn):
    conn = get_connection()
    cursor = conn.cursor()
    feats_json = json.dumps(txn.get('features', {}))
    attribs_json = json.dumps(txn.get('all_attributions', txn.get('top_drivers', [])))
    cursor.execute("""
        INSERT INTO transactions (timestamp, card_id, merchant, amount, risk_score, fraud_probability, is_fraud, decision, risk_level, recommended_action, features_json, attributions_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        txn.get('timestamp', datetime.now(timezone.utc).isoformat()),
        txn.get('card_id', 'CARD-UNKNOWN'),
        txn.get('merchant', 'Terminal Swipe'),
        float(txn.get('amount', 0.0)),
        float(txn.get('risk_score', 0.0)),
        float(txn.get('fraud_probability', 0.0)),
        1 if txn.get('is_fraud') else 0,
        txn.get('decision', 'APPROVED'),
        txn.get('risk_level', 'LOW'),
        txn.get('recommended_action', 'AUTO_APPROVE'),
        feats_json,
        attribs_json
    ))
    txn_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return txn_id

def get_all_transactions(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        feats = json.loads(r['features_json']) if r['features_json'] else {}
        attribs = json.loads(r['attributions_json']) if r['attributions_json'] else []
        results.append({
            'id': r['id'],
            'timestamp': r['timestamp'],
            'card_id': r['card_id'],
            'merchant': r['merchant'],
            'amount': r['amount'],
            'risk_score': r['risk_score'],
            'fraud_probability': r['fraud_probability'],
            'is_fraud': bool(r['is_fraud']),
            'decision': r['decision'],
            'risk_level': r['risk_level'],
            'recommended_action': r['recommended_action'],
            'features': feats,
            'all_attributions': attribs,
            'top_drivers': attribs[:5]
        })
    return results

def block_card_db(card_id, reason="High-Risk Fraud Interdiction", operator="FRAUD-OPERATOR"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO blocked_cards (card_id, blocked_at, reason, operator)
        VALUES (?, ?, ?, ?)
    """, (card_id, datetime.now(timezone.utc).isoformat(), reason, operator))
    conn.commit()
    conn.close()

def unblock_card_db(card_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_cards WHERE card_id = ?", (card_id,))
    conn.commit()
    conn.close()

def get_blocked_cards_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocked_cards ORDER BY blocked_at DESC")
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

def get_model_benchmarks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM model_benchmarks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
