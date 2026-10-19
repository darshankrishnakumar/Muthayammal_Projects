import os
import math
import time
import json
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import database
from nids_model import get_nids_engine

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Initialize DB on startup
database.init_db()
database.seed_database()

# Load inference engine
engine = get_nids_engine()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    stats = database.get_dashboard_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'Enterprise AI Network Intrusion Detection System (NIDS)',
        'architecture': 'Dual-Engine Deep Learning: PyTorch Autoencoder Anomaly + 17D Enriched Deep Classifier',
        'database_backend': 'SQLite ACID Relational DB (network_nids.db)',
        'dataset_benchmark': 'NSL-KDD & CICIDS2018 Reference Matrix (6,000 Verified Flow Corpus)',
        'port': 5026,
        'model_metadata': engine.metadata,
        'monitored_flows_count': stats['total_flows_inspected'],
        'quarantined_ips_count': stats['active_quarantine_count'],
        'attack_taxonomy': engine.classes
    })

@app.route('/api/model/metadata', methods=['GET'])
def model_metadata():
    return jsonify(engine.metadata)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = database.get_dashboard_stats()
    # Add dynamic network throughput variance
    stats['system_throughput_pps'] = random.randint(580, 750)
    stats['bandwidth_mbps'] = round(random.uniform(68.5, 84.2), 2)
    return jsonify(stats)

@app.route('/api/stream/next', methods=['GET'])
def stream_next_flow():
    """Generate next realistic network flow in simulated real-time stream."""
    attack_chance = random.random()
    if attack_chance < 0.15:
        # SYN flood packet
        src_ip = f"194.26.{random.randint(10,250)}.{random.randint(2,254)}"
        flow = {
            'src_ip': src_ip,
            'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'HTTP', 'flag': 'S0',
            'duration': 0.002, 'src_bytes': 64, 'dst_bytes': 0,
            'count': random.randint(180, 480), 'srv_count': random.randint(180, 480),
            'serror_rate': 0.98, 'rerror_rate': 0.0, 'same_srv_rate': 1.0,
            'diff_srv_rate': 0.0, 'dst_host_count': 255, 'dst_host_srv_count': 255,
            'dst_host_same_src_port_rate': 0.95
        }
    elif attack_chance < 0.25:
        # Port scan probe
        src_ip = f"185.190.{random.randint(1,100)}.{random.randint(2,254)}"
        flow = {
            'src_ip': src_ip,
            'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'MULTI_PORT', 'flag': 'REJ',
            'duration': 0.03, 'src_bytes': 44, 'dst_bytes': 0,
            'count': random.randint(90, 210), 'srv_count': random.randint(1, 3),
            'serror_rate': 0.15, 'rerror_rate': 0.92, 'same_srv_rate': 0.05,
            'diff_srv_rate': 0.95, 'dst_host_count': 200, 'dst_host_srv_count': 3,
            'dst_host_same_src_port_rate': 0.0
        }
    elif attack_chance < 0.30:
        # SSH Brute Force
        src_ip = f"198.51.100.{random.randint(10, 200)}"
        flow = {
            'src_ip': src_ip,
            'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'SSH', 'flag': 'SF',
            'duration': round(random.uniform(0.8, 2.2), 3),
            'src_bytes': random.randint(400, 750), 'dst_bytes': random.randint(300, 600),
            'count': random.randint(40, 85), 'srv_count': random.randint(40, 85),
            'serror_rate': 0.0, 'rerror_rate': round(random.uniform(0.4, 0.7), 2),
            'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
            'dst_host_count': 30, 'dst_host_srv_count': 30,
            'dst_host_same_src_port_rate': 0.45
        }
    else:
        # Normal user browsing
        services = [("HTTPS", 443), ("HTTP", 80), ("DNS", 53), ("SMTP", 25)]
        srv, port = random.choice(services)
        src_ip = f"192.168.1.{random.randint(100, 240)}"
        flow = {
            'src_ip': src_ip,
            'dst_ip': '10.0.0.5', 'protocol': 'TCP' if srv != 'DNS' else 'UDP', 'service': srv, 'flag': 'SF',
            'duration': round(random.uniform(0.2, 3.5), 3),
            'src_bytes': random.randint(300, 2500),
            'dst_bytes': random.randint(800, 18000),
            'count': random.randint(1, 8), 'srv_count': random.randint(1, 8),
            'serror_rate': 0.0, 'rerror_rate': 0.0, 'same_srv_rate': 0.95,
            'diff_srv_rate': 0.05, 'dst_host_count': random.randint(20, 150),
            'dst_host_srv_count': random.randint(18, 140),
            'dst_host_same_src_port_rate': round(random.uniform(0.01, 0.1), 3)
        }

    # Evaluate using PyTorch Deep Model
    eval_res = engine.evaluate(flow)
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **flow,
        **eval_res
    }
    flow_id = database.insert_flow(record)
    record['id'] = flow_id
    return jsonify(record)

@app.route('/api/simulate/attack', methods=['POST'])
def simulate_attack():
    """Inject specific known cyber attack vector."""
    data = request.json or {}
    attack_type = data.get('attack_type', 'SYN_Flood')

    if attack_type == 'SYN_Flood':
        flow = {
            'src_ip': '203.0.113.89', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'HTTP', 'flag': 'S0',
            'duration': 0.001, 'src_bytes': 64, 'dst_bytes': 0, 'count': 450, 'srv_count': 450,
            'serror_rate': 1.0, 'rerror_rate': 0.0, 'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
            'dst_host_count': 255, 'dst_host_srv_count': 255, 'dst_host_same_src_port_rate': 0.98
        }
    elif attack_type == 'Port_Scan':
        flow = {
            'src_ip': '198.51.100.42', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'NMAP_PROBE', 'flag': 'REJ',
            'duration': 0.05, 'src_bytes': 48, 'dst_bytes': 0, 'count': 180, 'srv_count': 2,
            'serror_rate': 0.1, 'rerror_rate': 0.95, 'same_srv_rate': 0.02, 'diff_srv_rate': 0.98,
            'dst_host_count': 255, 'dst_host_srv_count': 2, 'dst_host_same_src_port_rate': 0.0
        }
    elif attack_type == 'SSH_BruteForce':
        flow = {
            'src_ip': '192.0.2.115', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'SSH', 'flag': 'SF',
            'duration': 1.1, 'src_bytes': 540, 'dst_bytes': 420, 'count': 65, 'srv_count': 65,
            'serror_rate': 0.0, 'rerror_rate': 0.55, 'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
            'dst_host_count': 40, 'dst_host_srv_count': 40, 'dst_host_same_src_port_rate': 0.5
        }
    elif attack_type == 'Mirai_Botnet':
        flow = {
            'src_ip': '198.18.0.77', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'C2_BEACON', 'flag': 'SF',
            'duration': 35.0, 'src_bytes': 128, 'dst_bytes': 128, 'count': 2, 'srv_count': 1,
            'serror_rate': 0.0, 'rerror_rate': 0.0, 'same_srv_rate': 0.5, 'diff_srv_rate': 0.5,
            'dst_host_count': 5, 'dst_host_srv_count': 1, 'dst_host_same_src_port_rate': 1.0
        }
    elif attack_type == 'Zero_Day':
        flow = {
            'src_ip': '192.0.2.204', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'SHELLCODE', 'flag': 'RSTOS0',
            'duration': 0.15, 'src_bytes': 28500, 'dst_bytes': 80, 'count': 15, 'srv_count': 1,
            'serror_rate': 0.45, 'rerror_rate': 0.45, 'same_srv_rate': 0.15, 'diff_srv_rate': 0.85,
            'dst_host_count': 25, 'dst_host_srv_count': 1, 'dst_host_same_src_port_rate': 0.2
        }
    elif attack_type == 'Buffer_Overflow':
        flow = {
            'src_ip': '198.51.100.99', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'TELNET', 'flag': 'SF',
            'duration': 8.5, 'src_bytes': 4500, 'dst_bytes': 3200, 'count': 3, 'srv_count': 1,
            'serror_rate': 0.0, 'rerror_rate': 0.0, 'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
            'dst_host_count': 12, 'dst_host_srv_count': 2, 'dst_host_same_src_port_rate': 0.05
        }
    else:
        # Normal web browsing
        flow = {
            'src_ip': '192.168.1.150', 'dst_ip': '10.0.0.5', 'protocol': 'TCP', 'service': 'HTTPS', 'flag': 'SF',
            'duration': 1.5, 'src_bytes': 950, 'dst_bytes': 8400, 'count': 2, 'srv_count': 2,
            'serror_rate': 0.0, 'rerror_rate': 0.0, 'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
            'dst_host_count': 80, 'dst_host_srv_count': 75, 'dst_host_same_src_port_rate': 0.02
        }

    eval_res = engine.evaluate(flow)
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **flow,
        **eval_res
    }
    flow_id = database.insert_flow(record)
    record['id'] = flow_id
    return jsonify(record)

@app.route('/api/analyze/flow', methods=['POST'])
def analyze_flow():
    """Analyze custom user-supplied network flow payload."""
    data = request.json or {}
    if not data:
        return jsonify({'error': 'Empty network flow payload'}), 400

    flow = {
        'src_ip': data.get('src_ip', '192.168.1.100'),
        'dst_ip': data.get('dst_ip', '10.0.0.5'),
        'protocol': data.get('protocol', 'TCP'),
        'service': data.get('service', 'HTTP'),
        'flag': data.get('flag', 'SF'),
        'duration': float(data.get('duration', 0.5)),
        'src_bytes': int(data.get('src_bytes', 500)),
        'dst_bytes': int(data.get('dst_bytes', 1200)),
        'count': int(data.get('count', 2)),
        'srv_count': int(data.get('srv_count', 2)),
        'serror_rate': float(data.get('serror_rate', 0.0)),
        'rerror_rate': float(data.get('rerror_rate', 0.0)),
        'same_srv_rate': float(data.get('same_srv_rate', 1.0)),
        'diff_srv_rate': float(data.get('diff_srv_rate', 0.0)),
        'dst_host_count': int(data.get('dst_host_count', 25)),
        'dst_host_srv_count': int(data.get('dst_host_srv_count', 25)),
        'dst_host_same_src_port_rate': float(data.get('dst_host_same_src_port_rate', 0.05))
    }

    eval_res = engine.evaluate(flow)
    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **flow,
        **eval_res
    }
    flow_id = database.insert_flow(record)
    record['id'] = flow_id
    return jsonify(record)

@app.route('/api/traffic/log', methods=['GET'])
def get_traffic_log():
    limit = int(request.args.get('limit', 50))
    flows = database.get_recent_flows(limit=limit)
    return jsonify(flows)

@app.route('/api/quarantine', methods=['GET', 'POST', 'DELETE'])
def handle_quarantine():
    if request.method == 'GET':
        active = database.get_active_quarantine()
        return jsonify(active)

    if request.method == 'POST':
        data = request.json or {}
        ip = data.get('ip')
        if not ip:
            return jsonify({'error': 'Missing IP address'}), 400
        reason = data.get('reason', 'Manual Operator Block')
        success = database.add_quarantine(ip, reason=reason)
        return jsonify({'success': success, 'ip': ip, 'status': 'QUARANTINED'})

    if request.method == 'DELETE':
        data = request.json or {}
        ip = data.get('ip')
        if not ip:
            return jsonify({'error': 'Missing IP address'}), 400
        removed = database.remove_quarantine(ip)
        if removed:
            return jsonify({'success': True, 'ip': ip, 'status': 'UNBLOCKED'})
        return jsonify({'error': 'IP not found in active quarantine'}), 404

@app.route('/api/firewall/rules', methods=['GET'])
def firewall_rules():
    rules = database.get_firewall_rules()
    return jsonify(rules)

if __name__ == '__main__':
    print("=" * 65)
    print("🚀 AI Network Intrusion Detection System (PROJECT-026)")
    print("🔒 Dedicated Port: Port 5026 (http://127.0.0.1:5026/)")
    print("🧠 Engine: PyTorch Deep Autoencoder + 17D Enriched Deep Classifier")
    print("💾 Database: SQLite ACID Ledger (network_nids.db)")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5026, debug=False)
