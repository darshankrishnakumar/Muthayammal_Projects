"""
Real-Time Sign Language Translation & Speech Synthesis
Flask REST API Backend (Port 5029)
Powered by PyTorch Dual Deep Models + SQLite WAL Mode Persistence
"""

import os
import sys
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import random

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import (
    init_db, seed_database, log_translation, log_speech,
    get_recent_translations, get_all_vocabulary, get_audit_logs, verify_wal_status
)
from sign_engine import get_engine

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(BACKEND_DIR, '..', 'frontend'))

# Initialize database and PyTorch engine
seed_database()
engine = get_engine()

# Seed initial translation history if empty
wal_info = verify_wal_status()
if wal_info['translation_sessions_count'] == 0:
    sample_seq = ['HELLO', 'I LOVE YOU', 'WATER', 'PLEASE', 'THANK YOU', 'DOCTOR', 'YES', 'WELCOME']
    vocab = get_all_vocabulary()
    for s in sample_seq:
        res = engine.predict_gesture(s)
        meta = vocab.get(s, {})
        res['category'] = meta.get('category', 'General')
        res['description'] = meta.get('description', '')
        res['icon'] = meta.get('icon', '✋')
        log_translation(str(uuid.uuid4())[:8], res)

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
    vocab = get_all_vocabulary()
    return jsonify({
        'status': 'healthy',
        'service': 'Real-Time Sign Language Translation & Speech Synthesis API',
        'port': 5029,
        'models': {
            'spatial_model': 'SignSpatialClassifier (Deep Residual Landmark Net)',
            'sequence_model': 'SignSequenceBiLSTM (Temporal BiLSTM Forecaster)',
            'weights_loaded': True,
            'device': str(engine.device)
        },
        'database': {
            'engine': 'SQLite',
            'journal_mode': wal_status['journal_mode'],
            'wal_enabled': wal_status['wal_enabled'],
            'sessions_count': wal_status['translation_sessions_count'],
            'vocabulary_count': len(vocab)
        },
        'vocabulary_size': len(vocab),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/recognize', methods=['POST'])
def recognize():
    data = request.json or {}
    sign_target = data.get('sign')
    raw_landmarks = data.get('landmarks')

    vocab = get_all_vocabulary()
    prediction = engine.predict_gesture(sign_hint=sign_target, raw_landmarks=raw_landmarks)

    meta = vocab.get(prediction['sign'], {})
    prediction['category'] = meta.get('category', 'General')
    prediction['description'] = meta.get('description', '')
    prediction['icon'] = meta.get('icon', '✋')
    prediction['speech_prompt'] = meta.get('speech_prompt', prediction['sign'])

    session_uuid = str(uuid.uuid4())[:8]
    inserted_id = log_translation(session_uuid, prediction)
    prediction['id'] = inserted_id
    prediction['session_uuid'] = session_uuid
    prediction['timestamp'] = datetime.now(timezone.utc).isoformat()

    return jsonify(prediction)

@app.route('/api/translate-sequence', methods=['POST'])
def translate_sequence():
    data = request.json or {}
    sequence_16 = data.get('sequence', [])
    res = engine.predict_temporal_sequence(sequence_16)
    return jsonify(res)

@app.route('/api/dictionary', methods=['GET'])
def get_dictionary():
    vocab = get_all_vocabulary()
    return jsonify(vocab)

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = int(request.args.get('limit', 30))
    history = get_recent_translations(limit=limit)
    return jsonify(history)

@app.route('/api/sentence', methods=['GET'])
def get_sentence():
    history = get_recent_translations(limit=10)
    words = [r['sign'] for r in reversed(history)]
    sentence = ' '.join(words)
    return jsonify({
        'sentence': sentence,
        'words': words,
        'word_count': len(words),
        'phonetic_speech': sentence.lower().capitalize() if sentence else ""
    })

@app.route('/api/speech/log', methods=['POST'])
def speech_log():
    data = request.json or {}
    spoken_text = data.get('text', '')
    voice = data.get('voice', 'en-US')
    rate = float(data.get('rate', 1.0))
    pitch = float(data.get('pitch', 1.0))
    status = data.get('status', 'COMPLETED')

    log_speech(spoken_text, voice=voice, rate=rate, pitch=pitch, status=status)
    return jsonify({'status': 'logged', 'text': spoken_text})

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
    port = int(os.environ.get('PORT', 5029))
    print(f"Starting Project 29 Sign Language Translation Backend on Port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
