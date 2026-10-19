import os
import sqlite3
import json
import csv
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fraud_graph.db")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        balance REAL NOT NULL,
        country TEXT NOT NULL,
        risk REAL NOT NULL,
        status TEXT NOT NULL,
        cluster TEXT NOT NULL,
        in_degree INTEGER DEFAULT 0,
        out_degree INTEGER DEFAULT 0,
        total_inflow REAL DEFAULT 0.0,
        total_outflow REAL DEFAULT 0.0,
        gnn_embedding TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        amount REAL NOT NULL,
        note TEXT,
        channel TEXT NOT NULL,
        is_suspicious INTEGER DEFAULT 0,
        pattern TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (source) REFERENCES accounts(id),
        FOREIGN KEY (target) REFERENCES accounts(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS syndicates (
        syndicate_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        pattern TEXT NOT NULL,
        threat_level TEXT NOT NULL,
        risk_score REAL NOT NULL,
        involved_volume_usd REAL NOT NULL,
        nodes_json TEXT NOT NULL,
        edges_json TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS frozen_sanctions (
        account_id TEXT PRIMARY KEY,
        frozen_at TEXT NOT NULL,
        reason TEXT NOT NULL,
        frozen_by TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()

    # Check if accounts table is populated
    cursor.execute("SELECT COUNT(*) FROM accounts")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_database(conn)
    conn.close()

def seed_database(conn):
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    accounts_csv = os.path.join(DATA_DIR, "accounts.csv")
    transactions_csv = os.path.join(DATA_DIR, "transactions.csv")

    if os.path.isfile(accounts_csv) and os.path.isfile(transactions_csv):
        print("Seeding SQLite database from generated CSV files...")
        with open(accounts_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                INSERT OR REPLACE INTO accounts 
                (id, name, type, balance, country, risk, status, cluster, in_degree, out_degree, total_inflow, total_outflow, gnn_embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["id"], row["name"], row["type"], float(row["balance"]), row["country"],
                    float(row["risk"]), row["status"], row["cluster"],
                    int(row["in_degree"]), int(row["out_degree"]),
                    float(row["total_inflow"]), float(row["total_outflow"]),
                    json.dumps([]), now_str
                ))

        with open(transactions_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                INSERT OR REPLACE INTO transactions
                (id, source, target, amount, note, channel, is_suspicious, pattern, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["id"], row["source"], row["target"], float(row["amount"]),
                    row.get("note", ""), row.get("channel", "ACH/CARD"),
                    int(row.get("is_suspicious", 0)), row.get("pattern", "NORMAL"),
                    row.get("timestamp", now_str)
                ))

    # Pre-seed syndicates
    pre_syndicates = [
        {
            "syndicate_id": "SYN-CYCLE-01",
            "name": "Transnational Circular Carousel Loop Alpha",
            "pattern": "Circular Laundering Cycle (A → B → C → D → A)",
            "threat_level": "CRITICAL",
            "risk_score": 0.98,
            "involved_volume_usd": 732000.00,
            "nodes": ["RING-201", "RING-202", "RING-203", "RING-204"],
            "edges": ["TX-RING-1-1", "TX-RING-1-2", "TX-RING-1-3", "TX-RING-1-4"],
            "description": "Multi-jurisdictional shell corporation carousel rotating capital across BVI, Cyprus, Panama, and Seychelles to fabricate legitimate invoice settlements."
        },
        {
            "syndicate_id": "SYN-SMURF-02",
            "name": "High-Fanout Structured Smurfing Ring Bravo",
            "pattern": "Structured Smurfing Fan-Out Layer",
            "threat_level": "CRITICAL",
            "risk_score": 0.96,
            "involved_volume_usd": 94800.00,
            "nodes": ["MULE-KING-01"] + [f"MULE-SMURF-1{m:02d}" for m in range(1, 11)],
            "edges": [f"TX-SMURF-1-{m}" for m in range(1, 11)],
            "description": "Central mixing nexus dispersing tranches of $8,900–$9,850 to 10 intermediary money mule proxies specifically tuned beneath the $10,000 BSA/CTR threshold."
        },
        {
            "syndicate_id": "SYN-FUNNEL-03",
            "name": "Offshore Asset Aggregation Funnel Charlie",
            "pattern": "Multi-Source Funnel Aggregation (Fan-In)",
            "threat_level": "HIGH",
            "risk_score": 0.91,
            "involved_volume_usd": 284000.00,
            "nodes": ["OFFSHORE-EXIT-01"] + [f"FEEDER-1{f:02d}" for f in range(1, 9)],
            "edges": [f"TX-FUNNEL-1-{f}" for f in range(1, 9)],
            "description": "Eight domestic feeder accounts aggregating retail deposits and liquidating them directly into an unverified Cayman Islands holding LLC."
        }
    ]

    for syn in pre_syndicates:
        cursor.execute("""
        INSERT OR REPLACE INTO syndicates
        (syndicate_id, name, pattern, threat_level, risk_score, involved_volume_usd, nodes_json, edges_json, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            syn["syndicate_id"], syn["name"], syn["pattern"], syn["threat_level"],
            syn["risk_score"], syn["involved_volume_usd"],
            json.dumps(syn["nodes"]), json.dumps(syn["edges"]), syn["description"]
        ))

    # Audit log
    cursor.execute("""
    INSERT INTO system_audit (action, entity_id, details, timestamp)
    VALUES (?, ?, ?, ?)
    """, ("DATABASE_INIT", "SYSTEM", "Initial database seeded with graph accounts, transactions, and syndicates.", now_str))

    conn.commit()

def get_all_nodes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    rows = cursor.fetchall()
    nodes = []
    for r in rows:
        d = dict(r)
        if d.get("gnn_embedding"):
            try:
                d["gnn_embedding"] = json.loads(d["gnn_embedding"])
            except:
                d["gnn_embedding"] = []
        else:
            d["gnn_embedding"] = []
        nodes.append(d)
    conn.close()
    return nodes

def get_all_edges():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    edges = [dict(r) for r in rows]
    conn.close()
    return edges

def get_node_by_id(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE id = ?", (nid,))
    row = cursor.fetchone()
    node = dict(row) if row else None
    if node and node.get("gnn_embedding"):
        try:
            node["gnn_embedding"] = json.loads(node["gnn_embedding"])
        except:
            node["gnn_embedding"] = []
    conn.close()
    return node

def get_inbound_edges(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE target = ?", (nid,))
    rows = cursor.fetchall()
    edges = [dict(r) for r in rows]
    conn.close()
    return edges

def get_outbound_edges(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE source = ?", (nid,))
    rows = cursor.fetchall()
    edges = [dict(r) for r in rows]
    conn.close()
    return edges

def get_all_syndicates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM syndicates")
    rows = cursor.fetchall()
    syndicates = []
    for r in rows:
        d = dict(r)
        d["nodes"] = json.loads(d["nodes_json"])
        d["edges"] = json.loads(d["edges_json"])
        syndicates.append(d)
    conn.close()
    return syndicates

def get_frozen_account_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_id FROM frozen_sanctions")
    rows = cursor.fetchall()
    frozen = set(r["account_id"] for r in rows)
    conn.close()
    return frozen

def freeze_account(nid, reason="Automated GNN AML Sanction", frozen_by="FinCEN Autonomous Interdiction Agent"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
    INSERT OR REPLACE INTO frozen_sanctions (account_id, frozen_at, reason, frozen_by)
    VALUES (?, ?, ?, ?)
    """, (nid, now_str, reason, frozen_by))

    cursor.execute("UPDATE accounts SET status = 'FROZEN', risk = 0.999 WHERE id = ?", (nid,))

    cursor.execute("""
    INSERT INTO system_audit (action, entity_id, details, timestamp)
    VALUES (?, ?, ?, ?)
    """, ("ACCOUNT_FREEZE", nid, f"Account frozen by {frozen_by}: {reason}", now_str))

    conn.commit()
    conn.close()
    return True

def unfreeze_account(nid, unfrozen_by="AML Compliance Officer"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    cursor.execute("DELETE FROM frozen_sanctions WHERE account_id = ?", (nid,))
    cursor.execute("UPDATE accounts SET status = 'ACTIVE', risk = 0.500 WHERE id = ?", (nid,))

    cursor.execute("""
    INSERT INTO system_audit (action, entity_id, details, timestamp)
    VALUES (?, ?, ?, ?)
    """, ("ACCOUNT_UNFREEZE", nid, f"Account unfrozen by {unfrozen_by}", now_str))

    conn.commit()
    conn.close()
    return True

def insert_dynamic_ring(ring_nodes, ring_edges, syndicate_info):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    for n in ring_nodes:
        cursor.execute("""
        INSERT OR REPLACE INTO accounts 
        (id, name, type, balance, country, risk, status, cluster, in_degree, out_degree, total_inflow, total_outflow, gnn_embedding, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            n["id"], n["name"], n["type"], n["balance"], n["country"],
            n["risk"], "ACTIVE", n.get("cluster", "DYNAMIC_RING"),
            0, 0, 0.0, 0.0, json.dumps(n.get("gnn_embedding", [])), now_str
        ))

    for e in ring_edges:
        cursor.execute("""
        INSERT OR REPLACE INTO transactions
        (id, source, target, amount, note, channel, is_suspicious, pattern, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["id"], e["source"], e["target"], e["amount"],
            e.get("note", "Dynamic Injection"), e.get("channel", "SWIFT WIRE"),
            1, e.get("pattern", "DYNAMIC_CYCLE"), e.get("timestamp", now_str)
        ))

    cursor.execute("""
    INSERT OR REPLACE INTO syndicates
    (syndicate_id, name, pattern, threat_level, risk_score, involved_volume_usd, nodes_json, edges_json, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        syndicate_info["syndicate_id"], syndicate_info["name"], syndicate_info["pattern"],
        syndicate_info["threat_level"], syndicate_info["risk_score"],
        syndicate_info["involved_volume_usd"], json.dumps(syndicate_info["nodes"]),
        json.dumps(syndicate_info["edges"]), syndicate_info["description"]
    ))

    cursor.execute("""
    INSERT INTO system_audit (action, entity_id, details, timestamp)
    VALUES (?, ?, ?, ?)
    """, ("INJECT_DYNAMIC_RING", syndicate_info["syndicate_id"], f"Injected dynamic ring with {len(ring_nodes)} nodes", now_str))

    conn.commit()
    conn.close()

def update_node_metrics_and_risks(evaluated_nodes):
    conn = get_connection()
    cursor = conn.cursor()
    for n in evaluated_nodes:
        cursor.execute("""
        UPDATE accounts SET 
            risk = ?, status = ?, in_degree = ?, out_degree = ?,
            total_inflow = ?, total_outflow = ?, gnn_embedding = ?
        WHERE id = ?
        """, (
            n["risk"], n["status"], n["in_degree"], n["out_degree"],
            n["total_inflow"], n["total_outflow"], json.dumps(n["gnn_embedding"]),
            n["id"]
        ))
    conn.commit()
    conn.close()

def get_audit_logs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_audit ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    logs = [dict(r) for r in rows]
    conn.close()
    return logs
