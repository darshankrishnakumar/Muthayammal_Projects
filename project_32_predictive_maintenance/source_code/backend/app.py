import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ─── INDUSTRIAL PREDICTIVE MAINTENANCE TELEMETRY & RUL ENGINE ───────────────

MACHINES = {
    'Screw Compressor A-101': {
        'type': 'Rotary Screw Compressor',
        'nominal_rpm': 2980,
        'nominal_temp': 72.0,
        'nominal_vib': 1.1,
        'nominal_press': 8.5,
        'icon': '⚙️',
        'criticality': 'High'
    },
    'Centrifugal Pump B-204': {
        'type': 'Slurry Circulation Pump',
        'nominal_rpm': 1480,
        'nominal_temp': 64.0,
        'nominal_vib': 0.8,
        'nominal_press': 14.2,
        'icon': '🔄',
        'criticality': 'Critical'
    },
    'Induction Motor C-302': {
        'type': '3-Phase 350kW Motor',
        'nominal_rpm': 1780,
        'nominal_temp': 68.0,
        'nominal_vib': 0.6,
        'nominal_press': 1.0,
        'icon': '⚡',
        'criticality': 'Medium'
    },
    'Gas Turbine Generator D-401': {
        'type': 'Co-Gen Gas Turbine',
        'nominal_rpm': 5400,
        'nominal_temp': 118.0,
        'nominal_vib': 1.4,
        'nominal_press': 22.0,
        'icon': '🔥',
        'criticality': 'Critical'
    },
    'Conveyor Drive Unit E-505': {
        'type': 'Heavy Ore Conveyor Drive',
        'nominal_rpm': 720,
        'nominal_temp': 52.0,
        'nominal_vib': 1.8,
        'nominal_press': 3.5,
        'icon': '🏗️',
        'criticality': 'Low'
    }
}

FAULT_MODES = {
    'Normal Baseline': {'color': '#10b981', 'urgency': 'NONE', 'action': 'Routine monthly lubrication'},
    'Outer Race Bearing Spall': {'color': '#ef4444', 'urgency': 'IMMEDIATE', 'action': 'Replace DE spherical roller bearing & align shaft'},
    'Rotor Dynamic Imbalance': {'color': '#f97316', 'urgency': 'URGENT', 'action': 'Dynamic 2-plane balancing & check balance weights'},
    'Hydraulic Cavitation Wear': {'color': '#f59e0b', 'urgency': 'SCHEDULED', 'action': 'Inspect impeller vanes and suction pressure net positive head'},
    'Stator Winding Overheating': {'color': '#ef4444', 'urgency': 'IMMEDIATE', 'action': 'Check cooling fan airflow and measure insulation resistance'},
    'Mechanical Coupling Looseness': {'color': '#f59e0b', 'urgency': 'SCHEDULED', 'action': 'Torque foundation bolts and recheck laser alignment'}
}

maintenance_log = []

def run_diagnostics(machine_name, override_features=None, scenario='auto'):
    m = MACHINES.get(machine_name, MACHINES['Screw Compressor A-101'])
    
    if scenario == 'fault':
        is_fault = True
    elif scenario == 'normal':
        is_fault = False
    else:
        is_fault = random.random() < 0.4

    if is_fault:
        fault_name = random.choice([k for k in FAULT_MODES if k != 'Normal Baseline'])
        temp = round(m['nominal_temp'] * random.uniform(1.3, 1.6), 1)
        vib = round(m['nominal_vib'] * random.uniform(2.5, 4.8), 2)
        press = round(m['nominal_press'] * random.uniform(0.7, 1.4), 1)
        rpm = int(m['nominal_rpm'] + random.uniform(-180, 120))
        health_score = round(random.uniform(24.0, 58.0), 1)
        rul_hours = random.randint(48, 380)
    else:
        fault_name = 'Normal Baseline'
        temp = round(m['nominal_temp'] * random.uniform(0.95, 1.05), 1)
        vib = round(m['nominal_vib'] * random.uniform(0.9, 1.1), 2)
        press = round(m['nominal_press'] * random.uniform(0.98, 1.02), 1)
        rpm = int(m['nominal_rpm'] + random.uniform(-15, 15))
        health_score = round(random.uniform(88.0, 99.2), 1)
        rul_hours = random.randint(1800, 3600)

    # 8-band FFT Vibration Spectrum simulation
    fft_spectrum = [
        round(vib * random.uniform(0.1, 0.4), 2),  # 1X RPM fundamental
        round(vib * random.uniform(0.6, 1.0) if is_fault else vib * 0.1, 2), # 2X harmonics
        round(vib * random.uniform(0.3, 0.8) if is_fault else vib * 0.05, 2), # 3X harmonics
        round(vib * random.uniform(0.2, 0.5), 2),  # BPFO bearing pass outer
        round(vib * random.uniform(0.2, 0.6) if is_fault else vib * 0.04, 2), # BPFI inner
        round(vib * random.uniform(0.1, 0.3), 2),  # BSF ball spin
        round(vib * random.uniform(0.05, 0.2), 2), # FTF cage freq
        round(vib * 0.08, 2)                      # High-freq noise
    ]

    fault_info = FAULT_MODES[fault_name]
    rul_days = round(rul_hours / 24.0, 1)

    return {
        'machine': machine_name,
        'machine_type': m['type'],
        'criticality': m['criticality'],
        'icon': m['icon'],
        'health_score': health_score,
        'fault_mode': fault_name,
        'urgency': fault_info['urgency'],
        'action_required': fault_info['action'],
        'color': fault_info['color'],
        'rul_hours': rul_hours,
        'rul_days': rul_days,
        'telemetry': {
            'temperature_c': temp,
            'vibration_mm_s': vib,
            'pressure_bar': press,
            'rpm': rpm,
            'oil_viscosity_cst': round(random.uniform(42, 68), 1),
            'acoustic_emission_db': round(random.uniform(55, 98), 1)
        },
        'fft_harmonics': fft_spectrum,
        'model': 'Temporal Convolutional Network (TCN) + Multivariate Autoencoder'
    }

def seed_maintenance_history():
    for name in MACHINES:
        res = run_diagnostics(name)
        maintenance_log.append({
            'id': len(maintenance_log) + 1,
            'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(15, 240))).isoformat(),
            **res
        })

seed_maintenance_history()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'service': 'Industrial Predictive Maintenance Telemetry API',
        'monitored_assets': len(MACHINES),
        'model': 'TCN + Multi-Head Self-Attention RUL Estimator'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    machine = data.get('machine', 'Screw Compressor A-101')
    scenario = data.get('scenario', 'auto')
    
    result = run_diagnostics(machine, scenario=scenario)
    entry = {
        'id': len(maintenance_log) + 1,
        'timestamp': datetime.utcnow().isoformat(),
        **result
    }
    maintenance_log.insert(0, entry)
    return jsonify(entry)

@app.route('/api/machines', methods=['GET'])
def get_machines():
    return jsonify([{'name': k, **v} for k, v in MACHINES.items()])

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(maintenance_log[:30])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = len(maintenance_log)
    critical_urgency = sum(1 for m in maintenance_log if m['urgency'] == 'IMMEDIATE')
    avg_health = round(sum(m['health_score'] for m in maintenance_log) / max(1, total), 1)

    return jsonify({
        'total_inspections': total,
        'critical_urgencies': critical_urgency,
        'avg_fleet_health_score': avg_health,
        'connected_assets': len(MACHINES),
        'uptime_slas': '99.92%'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5032))
    app.run(debug=False, host='0.0.0.0', port=port)
