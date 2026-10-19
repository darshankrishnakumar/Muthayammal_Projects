import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone

# Add local directory to path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, seed_database, get_zones, get_history,
    get_stats, create_dispatch, get_dispatches, get_audit_logs, log_audit
)
from flood_engine import flood_engine, BASIN_DEFAULTS

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Ensure database is initialized on startup
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
        'service': 'Geospatial Flood Risk & Early Warning API',
        'port': int(os.environ.get('PORT', 5031)),
        'monitored_basins': len(get_zones()),
        'model': 'PyTorch Residual FloodNet + Inundation Regressor',
        'total_assessments': stats.get('total_assessments', 0),
        'storage': 'SQLite WAL Mode ACID Persistence'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json or {}
    zone = data.get('zone', 'Riverside Embankment District')
    
    # Accept features either nested under 'features' or passed flat in request body
    features = data.get('features')
    if not features or not isinstance(features, dict):
        features = {
            'rainfall_mm': data.get('rainfall_mm', data.get('rainfall', 65.0)),
            'river_level_m': data.get('river_level_m', data.get('river_stage_m', 4.5)),
            'soil_moisture': data.get('soil_moisture', 0.65),
            'storm_surge_m': data.get('storm_surge_m', data.get('storm_surge', 0.4))
        }

    result = flood_engine.predict(zone, features, persist=True)
    return jsonify(result)

@app.route('/api/zones', methods=['GET'])
def list_zones():
    zones = get_zones()
    return jsonify(zones)

@app.route('/api/history', methods=['GET'])
def history():
    limit = request.args.get('limit', default=30, type=int)
    records = get_history(limit=limit)
    return jsonify(records)

@app.route('/api/stats', methods=['GET'])
def stats():
    st = get_stats()
    return jsonify(st)

@app.route('/api/dispatches', methods=['GET'])
def dispatches():
    limit = request.args.get('limit', default=20, type=int)
    return jsonify(get_dispatches(limit=limit))

@app.route('/api/dispatch', methods=['POST'])
def dispatch_emergency():
    data = request.json or {}
    zone = data.get('zone', 'Bay Coastal Lowlands')
    alert_level = data.get('alert_level', 'CRITICAL')
    team = data.get('dispatch_team', 'Rapid Flood Inundation Response')
    action = data.get('action_taken', 'Deploy high-capacity pumps & flood barriers')
    status = data.get('status', 'DEPLOYED')
    protocol = data.get('protocol', 'Mandatory evacuation and critical asset relocation')

    did = create_dispatch(zone, alert_level, team, action, status, protocol)
    return jsonify({
        'success': True,
        'dispatch_id': did,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'zone': zone,
        'alert_level': alert_level,
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
    return jsonify({'model': 'PyTorch Residual FloodNet + Inundation Regressor'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5031))
    app.run(debug=False, host='0.0.0.0', port=port)
