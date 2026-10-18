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


# ─── DRIVER DROWSINESS DETECTION ──────────────────────────────────────────────
# Real: Use dlib/MediaPipe FaceMesh + LSTM on EAR/MAR time series

DROWSINESS_STATES = ['Alert', 'Slightly Drowsy', 'Moderately Drowsy', 'Severely Drowsy']
detection_log = []

def calculate_ear_mar(landmarks):
    """Simulate Eye Aspect Ratio and Mouth Aspect Ratio calculation."""
    ear = round(random.uniform(0.15, 0.40), 4)   # < 0.25 = eye closure
    mar = round(random.uniform(0.10, 0.60), 4)   # > 0.40 = yawning
    head_pose = round(random.uniform(-15, 15), 2) # degrees
    return ear, mar, head_pose

def classify_drowsiness(ear, mar, head_pose):
    score = 0.0
    if ear < 0.20: score += 0.5
    elif ear < 0.25: score += 0.3
    if mar > 0.50: score += 0.3
    if abs(head_pose) > 10: score += 0.2
    score += random.uniform(-0.05, 0.1)
    score = max(0.0, min(1.0, score))
    if score < 0.25: state = 'Alert'
    elif score < 0.50: state = 'Slightly Drowsy'
    elif score < 0.75: state = 'Moderately Drowsy'
    else: state = 'Severely Drowsy'
    return score, state

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'service': 'Driver Drowsiness Detection API'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    image_data = data.get('image', '')
    driver_id = data.get('driver_id', 'DRIVER_001')
    landmarks = data.get('landmarks', [])
    ear, mar, head_pose = calculate_ear_mar(landmarks)
    drowsiness_score, state = classify_drowsiness(ear, mar, head_pose)
    alert_required = drowsiness_score > 0.5
    result = {
        'id': len(detection_log) + 1,
        'driver_id': driver_id,
        'drowsiness_score': round(drowsiness_score, 4),
        'drowsiness_state': state,
        'ear': ear,
        'mar': mar,
        'head_pose_degrees': head_pose,
        'alert_required': alert_required,
        'alert_message': '⚠️ DROWSINESS ALERT! Please rest!' if alert_required else '✅ Driver is alert',
        'alert_type': 'AUDITORY_VISUAL' if drowsiness_score > 0.75 else 'VISUAL' if alert_required else 'NONE',
        'timestamp': datetime.utcnow().isoformat(),
        'model': 'Facial Landmarks + LSTM'
    }
    detection_log.append(result)
    return jsonify(result)

@app.route('/api/log', methods=['GET'])
def get_log():
    return jsonify(detection_log[-50:])

@app.route('/api/stats', methods=['GET'])
def stats():
    total = len(detection_log)
    alerts = sum(1 for d in detection_log if d['alert_required'])
    return jsonify({'total_frames': total, 'drowsiness_alerts': alerts, 'alert_rate': round(alerts/total*100, 1) if total else 0})

if __name__ == '__main__':
    app.run(debug=True, port=5035)
