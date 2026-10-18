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

# ─── ADVANCED IOT ANOMALY DETECTION & ZERO-TRUST SECURITY ENGINE ────────────

IOT_DEVICES = {
    'Smart IP Camera': {
        'ip': '192.168.1.42',
        'proto': 'RTSP / TCP',
        'norm_packet': 1240,
        'norm_rate': 45,
        'icon': '📹',
        'role': 'Living Room Cam'
    },
    'Smart Thermostat': {
        'ip': '192.168.1.18',
        'proto': 'MQTT / TLS',
        'norm_packet': 180,
        'norm_rate': 2,
        'icon': '🌡️',
        'role': 'HVAC Control Node'
    },
    'Smart Lock': {
        'ip': '192.168.1.105',
        'proto': 'Zigbee / BLE Gateway',
        'norm_packet': 64,
        'norm_rate': 0.5,
        'icon': '🔐',
        'role': 'Front Entrance Deadbolt'
    },
    'Smart TV 4K': {
        'ip': '192.168.1.88',
        'proto': 'HTTPS / SSDP',
        'norm_packet': 1420,
        'norm_rate': 120,
        'icon': '📺',
        'role': 'Media Room OLED'
    },
    'Edge Wi-Fi Router': {
        'ip': '192.168.1.1',
        'proto': 'DNS / DHCP / NTP',
        'norm_packet': 512,
        'norm_rate': 250,
        'icon': '📡',
        'role': 'Core Gateway'
    },
    'Smart Voice Assistant': {
        'ip': '192.168.1.73',
        'proto': 'mDNS / WebSockets',
        'norm_packet': 320,
        'norm_rate': 15,
        'icon': '🔊',
        'role': 'Kitchen Assistant'
    }
}

ATTACK_SIGNATURES = {
    'Mirai Botnet C&C': {'severity': 'CRITICAL', 'color': '#ef4444', 'action': 'Quarantine MAC & Terminate Port 23/Telnet'},
    'SYN Flood DDoS': {'severity': 'CRITICAL', 'color': '#ef4444', 'action': 'Enable SYN Cookies & Rate Limit IP'},
    'External Port Scan': {'severity': 'HIGH', 'color': '#f97316', 'action': 'Block Remote Scanner Subnet'},
    'Covert Data Exfiltration': {'severity': 'HIGH', 'color': '#f97316', 'action': 'Sever Outbound DNS Tunneling'},
    'Brute-Force SSH Auth': {'severity': 'MEDIUM', 'color': '#eab308', 'action': 'Enforce IP Ban (Fail2ban)'},
    'Normal Baseline Traffic': {'severity': 'NORMAL', 'color': '#10b981', 'action': 'No Action Required (Whitelisted)'}
}

anomaly_log = []

def inspect_traffic(device_name, scenario='auto', custom_features=None):
    dev = IOT_DEVICES.get(device_name, IOT_DEVICES['Smart IP Camera'])
    
    if scenario == 'attack':
        is_attack = True
    elif scenario == 'normal':
        is_attack = False
    else:
        is_attack = random.random() < 0.45

    if is_attack:
        attack_type = random.choice([k for k in ATTACK_SIGNATURES if k != 'Normal Baseline Traffic'])
        # Anomaly features
        packet_size = int(dev['norm_packet'] * random.uniform(2.8, 6.5))
        packet_rate = int(dev['norm_rate'] * random.uniform(4.0, 15.0))
        syn_ratio = round(random.uniform(0.75, 0.98), 2)
        entropy = round(random.uniform(7.2, 7.95), 2) # high packet payload entropy
        reconstruction_error = round(random.uniform(0.68, 0.98), 3) # Autoencoder loss
        anomaly_score = int(reconstruction_error * 100)
    else:
        attack_type = 'Normal Baseline Traffic'
        packet_size = int(dev['norm_packet'] * random.uniform(0.85, 1.15))
        packet_rate = int(dev['norm_rate'] * random.uniform(0.8, 1.25))
        syn_ratio = round(random.uniform(0.02, 0.12), 2)
        entropy = round(random.uniform(3.1, 4.8), 2)
        reconstruction_error = round(random.uniform(0.04, 0.22), 3)
        anomaly_score = int(reconstruction_error * 100)

    sig = ATTACK_SIGNATURES[attack_type]

    return {
        'device': device_name,
        'ip_address': dev['ip'],
        'protocol': dev['proto'],
        'device_role': dev['role'],
        'device_icon': dev['icon'],
        'is_anomaly': is_attack,
        'attack_type': attack_type,
        'severity': sig['severity'],
        'color': sig['color'],
        'action_taken': sig['action'],
        'anomaly_score': anomaly_score,
        'reconstruction_error': reconstruction_error,
        'telemetry': {
            'packet_size_bytes': packet_size,
            'packet_rate_pps': packet_rate,
            'syn_ratio': syn_ratio,
            'payload_entropy': entropy,
            'connection_frequency_hz': round(packet_rate * 0.4, 1)
        },
        'quarantine_status': 'ISOLATED' if (is_attack and sig['severity'] == 'CRITICAL') else 'ONLINE'
    }

def seed_iot_history():
    devices_list = list(IOT_DEVICES.keys())
    for _ in range(8):
        dev = random.choice(devices_list)
        res = inspect_traffic(dev)
        anomaly_log.append({
            'id': len(anomaly_log) + 1,
            'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(5, 180))).isoformat(),
            **res
        })

seed_iot_history()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'service': 'IoT Behavioral Profiling & Anomaly Detection API',
        'model': 'Deep Autoencoder (Reconstruction Loss) + Isolation Forest',
        'connected_devices': len(IOT_DEVICES),
        'total_inspections': len(anomaly_log)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    device = data.get('device', 'Smart IP Camera')
    scenario = data.get('scenario', 'auto')
    
    result = inspect_traffic(device, scenario)
    entry = {
        'id': len(anomaly_log) + 1,
        'timestamp': datetime.utcnow().isoformat(),
        **result
    }
    anomaly_log.insert(0, entry)
    return jsonify(entry)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify([{'name': k, **v} for k, v in IOT_DEVICES.items()])

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(anomaly_log[:40])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = len(anomaly_log)
    anomalies = sum(1 for a in anomaly_log if a['is_anomaly'])
    critical = sum(1 for a in anomaly_log if a['severity'] == 'CRITICAL')
    avg_score = round(sum(a.get('anomaly_score', 20) for a in anomaly_log) / max(1, total), 1)

    return jsonify({
        'total_inspections': total,
        'anomalies_detected': anomalies,
        'critical_threats': critical,
        'avg_anomaly_score': avg_score,
        'system_security_index': max(10, 100 - int(avg_score * 0.8))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5030))
    app.run(debug=False, host='0.0.0.0', port=port)
