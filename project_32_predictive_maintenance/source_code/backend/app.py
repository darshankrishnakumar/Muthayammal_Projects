import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone

# Add local directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    seed_database, get_machines, get_history,
    get_stats, create_work_order, get_work_orders, get_audit_logs, log_audit
)
from pdm_engine import pdm_engine, MACHINES_CONFIG

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Initialize and seed database on startup
seed_database()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ─── API ENDPOINTS ───────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    stats = get_stats()
    return jsonify({
        'status': 'running',
        'service': 'Industrial Predictive Maintenance Telemetry API',
        'port': int(os.environ.get('PORT', 5032)),
        'monitored_assets': len(get_machines()),
        'model': 'PyTorch Residual Health Classifier + RUL Regressor',
        'total_inspections': stats.get('total_inspections', 0),
        'storage': 'SQLite WAL Mode ACID Persistence'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    machine = data.get('machine', 'Screw Compressor A-101')
    scenario = data.get('scenario', 'auto')
    
    # Accept features nested or flat
    features = data.get('features')
    if not features or not isinstance(features, dict):
        features = {
            'temperature_c': data.get('temperature_c', data.get('temp')),
            'vibration_mm_s': data.get('vibration_mm_s', data.get('vibration_mms', data.get('vib'))),
            'pressure_bar': data.get('pressure_bar'),
            'pressure_psi': data.get('pressure_psi'),
            'rpm': data.get('rpm'),
            'oil_viscosity_cst': data.get('oil_viscosity_cst'),
            'acoustic_emission_db': data.get('acoustic_emission_db')
        }
        # Filter out None values
        features = {k: v for k, v in features.items() if v is not None}

    result = pdm_engine.analyze(machine, features=features, scenario=scenario, persist=True)
    return jsonify(result)

@app.route('/api/machines', methods=['GET'])
def list_machines():
    machines = get_machines()
    return jsonify(machines)

@app.route('/api/history', methods=['GET'])
def history():
    limit = request.args.get('limit', default=30, type=int)
    records = get_history(limit=limit)
    return jsonify(records)

@app.route('/api/stats', methods=['GET'])
def stats():
    st = get_stats()
    return jsonify(st)

@app.route('/api/work-orders', methods=['GET'])
def work_orders():
    limit = request.args.get('limit', default=20, type=int)
    return jsonify(get_work_orders(limit=limit))

@app.route('/api/work-order', methods=['POST'])
def dispatch_work_order():
    data = request.json or {}
    machine = data.get('machine', 'Gas Turbine Generator D-401')
    fault_mode = data.get('fault_mode', 'Outer Race Bearing Spall')
    urgency = data.get('urgency', 'IMMEDIATE')
    code = data.get('work_order_code', f"WO-{int(datetime.now(timezone.utc).timestamp())}")
    technician = data.get('technician', 'Senior Reliability Specialist')
    action = data.get('action_taken', 'Dispatched maintenance crew and diagnostic instruments')
    status = data.get('status', 'DISPATCHED')

    wo_id = create_work_order(machine, fault_mode, urgency, code, technician, action, status)
    return jsonify({
        'success': True,
        'work_order_id': wo_id,
        'work_order_code': code,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'machine': machine,
        'status': status
    })

@app.route('/api/audit-logs', methods=['GET'])
def audit_logs():
    limit = request.args.get('limit', default=50, type=int)
    return jsonify(get_audit_logs(limit=limit))

@app.route('/api/model/info', methods=['GET'])
def model_info():
    meta_path = os.path.join(os.path.dirname(__file__), 'model_metadata.json')
    if os.path.exists(meta_path):
        import json
        with open(meta_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'model': 'PyTorch Residual Health Classifier + RUL Regressor'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5032))
    app.run(debug=False, host='0.0.0.0', port=port)
