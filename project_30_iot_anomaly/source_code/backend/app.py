"""
AI-Based IoT Device Anomaly Detection for Smart Home Security
Flask REST API Backend (Port 5030)
Powered by PyTorch Dual Models (Deep Autoencoder + Threat Classifier) + SQLite WAL Mode
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import random

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import (
    init_db, seed_database, log_inspection, set_device_quarantine,
    get_recent_inspections, get_all_devices, get_security_stats,
    get_audit_logs, verify_wal_status
)
from anomaly_engine import get_engine, ATTACK_SIGNATURES

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(BACKEND_DIR, '..', 'frontend'))

# Initialize database and PyTorch engine
seed_database()
engine = get_engine()

# Seed initial history if empty
wal_info = verify_wal_status()
if wal_info['inspections_count'] == 0:
    devices = get_all_devices()
    for _ in range(12):
        dev = random.choice(devices)
        res = engine.analyze_traffic(dev, scenario='auto')
        log_inspection(res)

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Resource not found'}), 404

@app.route('/api/health', methods=['GET'])
def health():
    wal_status = verify_wal_status()
    devices = get_all_devices()
    return jsonify({
        'status': 'healthy',
        'service': 'IoT Behavioral Profiling & Anomaly Detection API',
        'port': 5030,
        'models': {
            'autoencoder': 'IoTAnomalyAutoencoder (Reconstruction Loss)',
            'classifier': 'IoTThreatClassifier (Residual Threat Signature)',
            'weights_loaded': True,
            'device': str(engine.device)
        },
        'database': {
            'engine': 'SQLite',
            'journal_mode': wal_status['journal_mode'],
            'wal_enabled': wal_status['wal_enabled'],
            'devices_count': wal_status['devices_count'],
            'inspections_count': wal_status['inspections_count']
        },
        'connected_devices': len(devices),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    device_name = data.get('device', 'Smart IP Camera')
    scenario = data.get('scenario', 'auto')
    raw_features = data.get('features')

    devices = {d['name']: d for d in get_all_devices()}
    dev_dict = devices.get(device_name, devices.get('Smart IP Camera', {
        'name': device_name, 'ip_address': '192.168.1.50', 'protocol': 'TCP',
        'role': 'IoT Endpoint', 'icon': '📱', 'norm_packet': 500, 'norm_rate': 20
    }))

    result = engine.analyze_traffic(dev_dict, scenario=scenario, raw_features=raw_features)
    inserted_id = log_inspection(result)
    result['id'] = inserted_id
    result['timestamp'] = datetime.now(timezone.utc).isoformat()

    return jsonify(result)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = get_all_devices()
    return jsonify(devices)

@app.route('/api/device/quarantine', methods=['POST'])
def quarantine_device():
    data = request.json or {}
    device_name = data.get('device')
    status = data.get('status', 'ISOLATED')
    set_device_quarantine(device_name, status)
    return jsonify({'status': 'updated', 'device': device_name, 'quarantine_status': status})

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = int(request.args.get('limit', 40))
    history = get_recent_inspections(limit=limit)
    return jsonify(history)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = get_security_stats()
    return jsonify(stats)

@app.route('/api/signatures', methods=['GET'])
def get_signatures():
    return jsonify(ATTACK_SIGNATURES)

@app.route('/api/loss-curve', methods=['GET'])
def get_loss_curve():
    history = get_recent_inspections(limit=25)
    points = []
    for h in reversed(history):
        points.append({
            'timestamp': h['timestamp'].split('T')[-1][:8],
            'reconstruction_error': h['reconstruction_error'],
            'threshold': 0.35,
            'is_anomaly': h['is_anomaly'],
            'attack_type': h['attack_type']
        })
    return jsonify(points)

@app.route('/api/metrics', methods=['GET'])
def metrics():
    return jsonify({
        'metadata': engine.metadata,
        'wal_status': verify_wal_status()
    })

@app.route('/api/audit-logs', methods=['GET'])
def audit_logs():
    logs = get_audit_logs(limit=50)
    return jsonify(logs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5030))
    print(f"Starting Project 30 IoT Anomaly Detection Backend on Port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
