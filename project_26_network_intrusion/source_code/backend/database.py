import os
import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "network_nids.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS network_flows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        src_ip TEXT NOT NULL,
        dst_ip TEXT NOT NULL,
        protocol TEXT NOT NULL,
        service TEXT NOT NULL,
        flag TEXT NOT NULL,
        duration REAL,
        src_bytes INTEGER,
        dst_bytes INTEGER,
        count INTEGER,
        srv_count INTEGER,
        serror_rate REAL,
        rerror_rate REAL,
        same_srv_rate REAL,
        reconstruction_error REAL,
        threshold_exceeded INTEGER,
        attack_name TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        confidence REAL,
        is_attack INTEGER NOT NULL,
        firewall_action TEXT NOT NULL,
        flow_summary TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quarantine_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT UNIQUE NOT NULL,
        reason TEXT NOT NULL,
        detected_at TEXT NOT NULL,
        packet_count INTEGER DEFAULT 1,
        status TEXT DEFAULT 'ACTIVE',
        unblocked_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS firewall_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        syntax TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        status TEXT DEFAULT 'APPLIED'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT NOT NULL,
        actor TEXT DEFAULT 'SYSTEM_NIDS'
    )
    """)

    conn.commit()
    conn.close()

def log_audit(event_type, details, severity="INFO", actor="SYSTEM_NIDS", cur=None):
    if cur:
        cur.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity, actor)
        VALUES (?, ?, ?, ?, ?)
        """, (datetime.now(timezone.utc).isoformat(), event_type, details, severity, actor))
    else:
        conn = get_connection()
        cur_internal = conn.cursor()
        cur_internal.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity, actor)
        VALUES (?, ?, ?, ?, ?)
        """, (datetime.now(timezone.utc).isoformat(), event_type, details, severity, actor))
        conn.commit()
        conn.close()

def insert_flow(flow_record):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO network_flows (
        timestamp, src_ip, dst_ip, protocol, service, flag,
        duration, src_bytes, dst_bytes, count, srv_count,
        serror_rate, rerror_rate, same_srv_rate,
        reconstruction_error, threshold_exceeded,
        attack_name, attack_type, category, severity,
        confidence, is_attack, firewall_action, flow_summary
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flow_record.get("timestamp", datetime.now(timezone.utc).isoformat()),
        flow_record.get("src_ip", "192.168.1.100"),
        flow_record.get("dst_ip", "10.0.0.5"),
        flow_record.get("protocol", "TCP"),
        flow_record.get("service", "HTTP"),
        flow_record.get("flag", "SF"),
        float(flow_record.get("duration", 0.0)),
        int(flow_record.get("src_bytes", 0)),
        int(flow_record.get("dst_bytes", 0)),
        int(flow_record.get("count", 1)),
        int(flow_record.get("srv_count", 1)),
        float(flow_record.get("serror_rate", 0.0)),
        float(flow_record.get("rerror_rate", 0.0)),
        float(flow_record.get("same_srv_rate", 1.0)),
        float(flow_record.get("reconstruction_error", 0.0)),
        1 if flow_record.get("threshold_exceeded") else 0,
        flow_record.get("attack_name", "Normal"),
        flow_record.get("attack_type", "Normal"),
        flow_record.get("category", "Benign"),
        flow_record.get("severity", "SAFE"),
        float(flow_record.get("confidence", 99.0)),
        1 if flow_record.get("is_attack") else 0,
        flow_record.get("firewall_action", "ALLOW"),
        flow_record.get("flow_summary", "")
    ))
    flow_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Auto-quarantine on CRITICAL attack after committing flow
    if flow_record.get("severity") == "CRITICAL" and flow_record.get("src_ip"):
        add_quarantine(
            ip_address=flow_record["src_ip"],
            reason=f"Automated Critical Threat: {flow_record.get('attack_name')}",
            packet_count=int(flow_record.get("count", 1))
        )

    return flow_id

def get_recent_flows(limit=50):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM network_flows ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def add_quarantine(ip_address, reason="Manual Block", packet_count=1):
    conn = get_connection()
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        cur.execute("""
        INSERT INTO quarantine_ledger (ip_address, reason, detected_at, packet_count, status)
        VALUES (?, ?, ?, ?, 'ACTIVE')
        ON CONFLICT(ip_address) DO UPDATE SET
            packet_count = packet_count + excluded.packet_count,
            status = 'ACTIVE'
        """, (ip_address, reason, now_iso, packet_count))

        # Generate and insert firewall rules
        iptables_cmd = f"iptables -A INPUT -s {ip_address} -j DROP"
        ufw_cmd = f"ufw deny from {ip_address} to any"
        cur.execute("""
        INSERT INTO firewall_rules (ip_address, rule_type, syntax, generated_at, status)
        VALUES (?, 'iptables', ?, ?, 'APPLIED')
        """, (ip_address, iptables_cmd, now_iso))
        cur.execute("""
        INSERT INTO firewall_rules (ip_address, rule_type, syntax, generated_at, status)
        VALUES (?, 'ufw', ?, ?, 'APPLIED')
        """, (ip_address, ufw_cmd, now_iso))

        # Log audit using the same active cursor
        cur.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity, actor)
        VALUES (?, 'IP_QUARANTINE', ?, 'WARN', 'SYSTEM_NIDS')
        """, (now_iso, f"Quarantined IP {ip_address}: {reason}"))

        conn.commit()
        success = True
    except Exception as e:
        conn.rollback()
        success = False
    finally:
        conn.close()
    return success

def remove_quarantine(ip_address):
    conn = get_connection()
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute("""
    UPDATE quarantine_ledger
    SET status = 'UNBLOCKED', unblocked_at = ?
    WHERE ip_address = ? AND status = 'ACTIVE'
    """, (now_iso, ip_address))
    rows_affected = cur.rowcount
    if rows_affected > 0:
        cur.execute("UPDATE firewall_rules SET status = 'REVOKED' WHERE ip_address = ?", (ip_address,))
        cur.execute("""
        INSERT INTO audit_log (timestamp, event_type, details, severity, actor)
        VALUES (?, 'IP_UNBLOCK', ?, 'INFO', 'SYSTEM_NIDS')
        """, (now_iso, f"Unblocked IP {ip_address} from active firewall rules"))
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_active_quarantine():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT ip_address as ip, reason, detected_at, packet_count
    FROM quarantine_ledger
    WHERE status = 'ACTIVE'
    ORDER BY id DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_firewall_rules():
    active = get_active_quarantine()
    ips = [item["ip"] for item in active]
    iptables_rules = [f"iptables -A INPUT -s {ip} -j DROP" for ip in ips]
    ufw_rules = [f"ufw deny from {ip} to any" for ip in ips]
    aws_nacl_rules = [
        {"RuleNumber": 100 + i, "Protocol": "-1", "RuleAction": "deny", "CidrBlock": f"{ip}/32"}
        for i, ip in enumerate(ips)
    ]
    return {
        "blocked_ips_count": len(ips),
        "iptables_script": "\n".join(iptables_rules) if iptables_rules else "# No active blocked IPs",
        "ufw_script": "\n".join(ufw_rules) if ufw_rules else "# No active blocked IPs",
        "aws_nacl_config": aws_nacl_rules
    }

def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM network_flows")
    total_flows = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM network_flows WHERE is_attack = 1")
    attacks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM network_flows WHERE severity = 'CRITICAL'")
    critical = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM quarantine_ledger WHERE status = 'ACTIVE'")
    active_quarantine = cur.fetchone()[0]

    cur.execute("SELECT category, COUNT(*) as cnt FROM network_flows GROUP BY category")
    breakdown = {row["category"]: row["cnt"] for row in cur.fetchall()}

    conn.close()

    threat_ratio = round((attacks / max(1, total_flows)) * 100, 1)
    normal_packets = total_flows - attacks

    return {
        "total_flows_inspected": total_flows,
        "attacks_intercepted": attacks,
        "normal_packets": normal_packets,
        "critical_threats": critical,
        "threat_ratio_percent": threat_ratio,
        "active_quarantine_count": active_quarantine,
        "category_breakdown": breakdown,
        "system_throughput_pps": 640,
        "bandwidth_mbps": 72.4
    }

def seed_database(force=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM network_flows")
    count = cur.fetchone()[0]
    conn.close()

    if count > 0 and not force:
        return

    # Seed initial baseline flows
    seeds = [
        {"src_ip": "192.168.1.105", "dst_ip": "10.0.0.5", "protocol": "TCP", "service": "HTTPS", "flag": "SF", "duration": 1.2, "src_bytes": 620, "dst_bytes": 4800, "count": 3, "srv_count": 3, "serror_rate": 0.0, "rerror_rate": 0.0, "same_srv_rate": 1.0, "attack_name": "Normal", "attack_type": "Normal", "category": "Benign", "severity": "SAFE", "confidence": 99.8, "is_attack": 0, "reconstruction_error": 0.0032, "threshold_exceeded": 0, "firewall_action": "ALLOW", "flow_summary": "TCP HTTPS [SF] • 620b in / 4800b out"},
        {"src_ip": "45.142.195.88", "dst_ip": "10.0.0.5", "protocol": "TCP", "service": "HTTP", "flag": "S0", "duration": 0.01, "src_bytes": 60, "dst_bytes": 0, "count": 280, "srv_count": 280, "serror_rate": 0.98, "rerror_rate": 0.0, "same_srv_rate": 1.0, "attack_name": "DoS SYN Flood", "attack_type": "DoS_SYN_Flood", "category": "Denial of Service", "severity": "CRITICAL", "confidence": 99.9, "is_attack": 1, "reconstruction_error": 0.0385, "threshold_exceeded": 1, "firewall_action": "BLOCK / DROP", "flow_summary": "TCP HTTP [S0] • 60b in / 0b out"},
        {"src_ip": "192.168.1.112", "dst_ip": "10.0.0.5", "protocol": "UDP", "service": "DNS", "flag": "SF", "duration": 0.05, "src_bytes": 74, "dst_bytes": 190, "count": 1, "srv_count": 1, "serror_rate": 0.0, "rerror_rate": 0.0, "same_srv_rate": 1.0, "attack_name": "Normal", "attack_type": "Normal", "category": "Benign", "severity": "SAFE", "confidence": 99.5, "is_attack": 0, "reconstruction_error": 0.0028, "threshold_exceeded": 0, "firewall_action": "ALLOW", "flow_summary": "UDP DNS [SF] • 74b in / 190b out"},
        {"src_ip": "185.220.101.4", "dst_ip": "10.0.0.5", "protocol": "TCP", "service": "OTHER", "flag": "REJ", "duration": 0.04, "src_bytes": 40, "dst_bytes": 0, "count": 140, "srv_count": 2, "serror_rate": 0.1, "rerror_rate": 0.95, "same_srv_rate": 0.08, "attack_name": "Probe PortScan", "attack_type": "Probe_PortScan", "category": "Reconnaissance", "severity": "HIGH", "confidence": 99.4, "is_attack": 1, "reconstruction_error": 0.0412, "threshold_exceeded": 1, "firewall_action": "BLOCK / DROP", "flow_summary": "TCP OTHER [REJ] • 40b in / 0b out"},
        {"src_ip": "198.51.100.23", "dst_ip": "10.0.0.5", "protocol": "TCP", "service": "SSH", "flag": "SF", "duration": 0.8, "src_bytes": 450, "dst_bytes": 380, "count": 48, "srv_count": 48, "serror_rate": 0.0, "rerror_rate": 0.45, "same_srv_rate": 1.0, "attack_name": "R2L SSH BruteForce", "attack_type": "R2L_SSH_BruteForce", "category": "Remote to Local", "severity": "CRITICAL", "confidence": 99.1, "is_attack": 1, "reconstruction_error": 0.0294, "threshold_exceeded": 1, "firewall_action": "BLOCK / DROP", "flow_summary": "TCP SSH [SF] • 450b in / 380b out"},
        {"src_ip": "192.168.1.120", "dst_ip": "10.0.0.5", "protocol": "TCP", "service": "HTTPS", "flag": "SF", "duration": 2.1, "src_bytes": 1100, "dst_bytes": 12800, "count": 4, "srv_count": 4, "serror_rate": 0.0, "rerror_rate": 0.0, "same_srv_rate": 1.0, "attack_name": "Normal", "attack_type": "Normal", "category": "Benign", "severity": "SAFE", "confidence": 99.7, "is_attack": 0, "reconstruction_error": 0.0036, "threshold_exceeded": 0, "firewall_action": "ALLOW", "flow_summary": "TCP HTTPS [SF] • 1100b in / 12800b out"}
    ]

    for s in seeds:
        insert_flow(s)

    # Initial system audit log
    log_audit("SYSTEM_BOOT", "AI Network Intrusion Detection System initialized with dual-engine ML and SQLite persistence", severity="INFO")

if __name__ == "__main__":
    init_db()
    seed_database()
    print("Database network_nids.db initialized and seeded successfully.")
