import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
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


# ─── TRAFFIC VIOLATION DETECTION ──────────────────────────────────────────────
# Real: Use YOLOv8 + DeepSORT tracking on CCTV footage; ANPR for license plates

VIOLATION_TYPES = ['Red Light Violation', 'Speeding', 'Wrong Way Driving', 'No Seatbelt',
                   'Mobile Phone Usage', 'Illegal Parking', 'No Helmet', 'Lane Violation']
VEHICLE_TYPES = ['Car', 'Motorcycle', 'Bus', 'Truck', 'Auto Rickshaw', 'Bicycle']

violation_log = []
fine_table = {
    'Red Light Violation': 1000, 'Speeding': 2000, 'Wrong Way Driving': 5000,
    'No Seatbelt': 500, 'Mobile Phone Usage': 1500, 'Illegal Parking': 500,
    'No Helmet': 1000, 'Lane Violation': 500
}

def detect_violations(frame_data, location):
    num_vehicles = random.randint(0, 4)
    detections = []
    for i in range(num_vehicles):
        vehicle_type = random.choice(VEHICLE_TYPES)
        plate = f"TN{random.randint(10,99)}A{random.randint(1000,9999)}"
        has_violation = random.random() < 0.35
        violation_type = random.choice(VIOLATION_TYPES) if has_violation else None
        speed = round(random.uniform(30, 120), 1)
        speed_limit = 60
        if speed > speed_limit and not has_violation:
            has_violation = True
            violation_type = 'Speeding'
        detections.append({
            'vehicle_id': i + 1,
            'vehicle_type': vehicle_type,
            'license_plate': plate,
            'speed_kmph': speed,
            'speed_limit': speed_limit,
            'violation_detected': has_violation,
            'violation_type': violation_type,
            'fine_amount': fine_table.get(violation_type, 0) if has_violation else 0,
            'confidence': round(random.uniform(0.78, 0.97), 3),
            'bbox': {'x': random.randint(50, 600), 'y': random.randint(50, 400), 'width': 120, 'height': 80}
        })
    return detections

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'service': 'Traffic Violation Detection API'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    frame_data = data.get('image', '')
    location = data.get('location', 'Intersection A')
    camera_id = data.get('camera_id', 'CAM_001')
    detections = detect_violations(frame_data, location)
    violations = [d for d in detections if d['violation_detected']]
    total_fines = sum(v['fine_amount'] for v in violations)
    result = {
        'id': len(violation_log) + 1,
        'camera_id': camera_id,
        'location': location,
        'vehicles_detected': len(detections),
        'violations_found': len(violations),
        'total_fine_amount': total_fines,
        'detections': detections,
        'timestamp': datetime.utcnow().isoformat(),
        'model': 'YOLOv8 + DeepSORT + ANPR'
    }
    violation_log.append(result)
    return jsonify(result)

@app.route('/api/violations', methods=['GET'])
def get_violations():
    return jsonify(violation_log[-30:])

@app.route('/api/stats', methods=['GET'])
def stats():
    total_scans = len(violation_log)
    total_violations = sum(r['violations_found'] for r in violation_log)
    total_revenue = sum(r['total_fine_amount'] for r in violation_log)
    return jsonify({
        'total_scans': total_scans,
        'total_violations': total_violations,
        'total_fine_revenue': total_revenue,
        'avg_violations_per_scan': round(total_violations / total_scans, 2) if total_scans else 0
    })

if __name__ == '__main__':
    app.run(debug=True, port=5037)
