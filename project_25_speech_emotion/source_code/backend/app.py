import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import database
from ser_model import ser_engine, EMOTION_META

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Initialize database on startup
database.init_db()

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
    stats = database.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'Multilingual Speech Emotion Recognition API',
        'architecture': '1D-CNN + Bi-LSTM with Self-Attention Pooling (DeepSERNet)',
        'supported_emotions': 7,
        'database_backend': 'SQLite ACID Relational DB (speech_emotion.db)',
        'total_audios_processed': stats['total_samples'],
        'model_metadata': ser_engine.metadata
    })

@app.route('/api/recognize', methods=['POST'])
def recognize():
    data = request.json or {}
    # Support both nested audio_info and flat payload
    if 'audio_info' in data and isinstance(data['audio_info'], dict):
        audio_info = data['audio_info']
    else:
        audio_info = data

    note = data.get('note', f"{audio_info.get('language', 'English')} spoken sample")
    
    # Run PyTorch deep learning inference
    result = ser_engine.predict_audio_features(audio_info)
    result['note'] = note

    # Persist in SQLite relational database
    session_id = database.save_audio_session(result)
    result['id'] = session_id

    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def get_history():
    sessions = database.get_recent_sessions(limit=40)
    return jsonify(sessions)

@app.route('/api/languages', methods=['GET'])
def get_languages():
    langs = database.get_languages()
    return jsonify(langs)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = database.get_stats()
    return jsonify(stats)

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    return jsonify({
        'architecture': '1D-CNN + Bi-LSTM + Self-Attention Pooling',
        'input_dimension': 40,
        'feature_breakdown': {
            'mfcc_means': 13,
            'mfcc_stds': 13,
            'pitch_f0_and_std': 2,
            'rms_energy': 1,
            'spectral_centroid': 1,
            'spectral_rolloff': 1,
            'zero_crossing_rate': 1,
            'jitter_and_shimmer': 2,
            'chroma_subbands': 4,
            'spectral_contrast': 2
        },
        'metadata': ser_engine.metadata
    })

@app.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    logs = database.get_audit_logs(limit=50)
    return jsonify(logs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5025))
    app.run(debug=False, host='0.0.0.0', port=port)
