import os
import json
import joblib
import numpy as np
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))

# ─── LOAD SERIALIZED NLP MODELS & METADATA ───────────────────────────────────

VEC_PATH = os.path.join(BACKEND_DIR, "tfidf_vectorizer.joblib")
CAT_MODEL_PATH = os.path.join(BACKEND_DIR, "category_model.joblib")
PRIO_MODEL_PATH = os.path.join(BACKEND_DIR, "priority_model.joblib")
META_PATH = os.path.join(BACKEND_DIR, "model_metadata.json")

print("[INFO] Initializing SQLite Database...")
database.init_db()

print("[INFO] Loading NLP vectorizer and calibrated classifiers...")
try:
    vectorizer = joblib.load(VEC_PATH)
    category_model = joblib.load(CAT_MODEL_PATH)
    priority_model = joblib.load(PRIO_MODEL_PATH)
    with open(META_PATH, 'r') as f:
        model_metadata = json.load(f)
    print(f"[INFO] Successfully loaded models. Vocab size: {len(vectorizer.vocabulary_)} | Trained at: {model_metadata.get('timestamp')}")
except Exception as e:
    print(f"[WARN] Error loading trained model artifacts: {e}. Running fallback training...")
    from data.train_and_save_models import generate_complaints_dataset, train_and_evaluate_models
    df = generate_complaints_dataset(3000)
    train_and_evaluate_models(df)
    vectorizer = joblib.load(VEC_PATH)
    category_model = joblib.load(CAT_MODEL_PATH)
    priority_model = joblib.load(PRIO_MODEL_PATH)
    with open(META_PATH, 'r') as f:
        model_metadata = json.load(f)

# ─── TAXONOMY & ROUTING CONFIGURATION ────────────────────────────────────────

CATEGORIES = {
    'payment_issue': {
        'label': 'Payment & Billing Dispute',
        'dept': 'FinOps Billing & Fraud Team',
        'icon': '💳',
        'keywords': ['payment', 'transaction', 'charge', 'billing', 'refund', 'money', 'fee', 'overcharge', 'invoice', 'credit card', 'bank', 'double billed', 'unauthorized']
    },
    'product_complaint': {
        'label': 'Product Defect & Hardware RMA',
        'dept': 'Quality Engineering & RMA Desk',
        'icon': '📦',
        'keywords': ['product', 'defective', 'broken', 'damaged', 'quality', 'item', 'malfunction', 'hardware', 'cracked', 'faulty', 'scratched', 'dead on arrival']
    },
    'delivery_problem': {
        'label': 'Logistics & Dispatch Delay',
        'dept': 'Global Supply Chain & Logistics',
        'icon': '🚚',
        'keywords': ['delivery', 'shipping', 'late', 'package', 'courier', 'tracking', 'transit', 'delayed', 'customs', 'lost in transit', 'dispatch', 'carrier']
    },
    'technical_issue': {
        'label': 'Software Bug & Platform Outage',
        'dept': 'Tier-3 Engineering & DevOps',
        'icon': '💻',
        'keywords': ['app', 'website', 'error', 'crash', 'bug', 'glitch', 'api', 'server', 'timeout', '500', '404', 'exception', 'slow load', 'latency']
    },
    'account_issue': {
        'label': 'IAM & Account Security',
        'dept': 'Identity & Access Management (IAM)',
        'icon': '🔐',
        'keywords': ['account', 'access', 'locked', 'suspended', 'profile', 'username', 'password', '2fa', 'mfa', 'unauthorized login', 'security alert', 'breach']
    },
    'service_dissatisfaction': {
        'label': 'Customer Experience & SLA Escalation',
        'dept': 'Executive Customer Relations',
        'icon': '🤝',
        'keywords': ['service', 'rude', 'unhelpful', 'slow', 'dissatisfied', 'complaint', 'agent', 'support', 'wait time', 'disappointed', 'terrible experience', 'escalate']
    }
}

PRIORITY_RULES = {
    'critical': {
        'sla_hours': 0.5,
        'badge_color': '#ef4444',
        'urgency_base': 92
    },
    'high': {
        'sla_hours': 2.0,
        'badge_color': '#f97316',
        'urgency_base': 76
    },
    'medium': {
        'sla_hours': 8.0,
        'badge_color': '#eab308',
        'urgency_base': 52
    },
    'low': {
        'sla_hours': 24.0,
        'badge_color': '#10b981',
        'urgency_base': 24
    }
}

# ─── REAL INFERENCE ENGINE ───────────────────────────────────────────────────

def classify_complaint(text):
    text_clean = text.strip()
    
    # Vectorize complaint text with trained TF-IDF
    X_vec = vectorizer.transform([text_clean])

    # 1. Category Classification via Calibrated Model
    cat_probs_raw = category_model.predict_proba(X_vec)[0]
    cat_classes = list(category_model.classes_)
    
    probabilities = {}
    for idx, cat_name in enumerate(cat_classes):
        probabilities[cat_name] = round(float(cat_probs_raw[idx]), 4)
    
    # Fill any missing categories if taxonomy differs
    for cat_key in CATEGORIES:
        if cat_key not in probabilities:
            probabilities[cat_key] = 0.001

    best_cat_idx = int(np.argmax(cat_probs_raw))
    best_cat = cat_classes[best_cat_idx]
    confidence = round(float(cat_probs_raw[best_cat_idx]), 4)

    # 2. Priority Classification via Calibrated Model
    prio_probs_raw = priority_model.predict_proba(X_vec)[0]
    prio_classes = list(priority_model.classes_)
    best_prio_idx = int(np.argmax(prio_probs_raw))
    priority = prio_classes[best_prio_idx]

    # Keyword matching for explainability from model vocabulary
    feature_names = vectorizer.get_feature_names_out()
    nonzero_indices = X_vec.nonzero()[1]
    matched_features = [feature_names[i] for i in nonzero_indices]
    
    # Also cross-reference with domain category keywords
    cat_meta = CATEGORIES.get(best_cat, CATEGORIES['service_dissatisfaction'])
    domain_kws = [kw for kw in cat_meta['keywords'] if kw in text_clean.lower()]
    all_kws = list(dict.fromkeys(domain_kws + matched_features))[:6]

    # 3. Deterministic Urgency & Sentiment Calculation
    prio_meta = PRIORITY_RULES.get(priority, PRIORITY_RULES['medium'])
    # Urgency derived deterministically from priority base + confidence factor
    urgency_score = min(100, max(10, int(prio_meta['urgency_base'] + (confidence - 0.5) * 10)))
    
    # Sentiment calculation based on priority and urgency
    if priority == 'critical':
        sentiment_score = round(-0.75 - (urgency_score / 400.0), 2)
    elif priority == 'high':
        sentiment_score = round(-0.45 - (urgency_score / 500.0), 2)
    elif priority == 'medium':
        sentiment_score = round(-0.15 - (urgency_score / 600.0), 2)
    else:
        sentiment_score = round(0.05 + ((100 - urgency_score) / 500.0), 2)

    sla_hours = prio_meta['sla_hours']
    now_utc = datetime.now(timezone.utc)
    sla_deadline = (now_utc + timedelta(hours=sla_hours)).strftime("%Y-%m-%d %H:%M UTC")

    summary = f"Customer flagged {cat_meta['label'].lower()} needing routing to {cat_meta['dept']} with {priority.upper()} priority."

    return {
        'category': best_cat,
        'category_label': cat_meta['label'],
        'category_icon': cat_meta['icon'],
        'department': cat_meta['dept'],
        'priority': priority,
        'priority_label': priority.upper(),
        'confidence': confidence,
        'probabilities': probabilities,
        'matched_keywords': all_kws,
        'urgency_score': urgency_score,
        'sentiment_score': sentiment_score,
        'sla_hours': sla_hours,
        'sla_deadline': sla_deadline,
        'summary': summary
    }

# ─── HTTP ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/health', methods=['GET'])
def health():
    stats = database.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'AI Customer Complaint & Priority Router API',
        'model': model_metadata.get('category_model', {}).get('algorithm', 'Calibrated Logistic Regression'),
        'accuracy_pct': round(model_metadata.get('category_model', {}).get('accuracy', 0.99) * 100, 2),
        'macro_f1': model_metadata.get('category_model', {}).get('macro_f1', 0.99),
        'categories_supported': len(CATEGORIES),
        'total_tickets_logged': stats['total'],
        'database': 'SQLite 3 (Transactional ACID)',
        'server_timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.json or {}
    complaint_text = data.get('complaint', '').strip()
    if not complaint_text:
        return jsonify({'error': 'Empty complaint text'}), 400

    analysis = classify_complaint(complaint_text)
    
    ticket_payload = {
        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        'complaint': complaint_text,
        'status': 'PENDING',
        'notes': 'Automatically ingested via NLP Triage Engine',
        'user_ip': request.remote_addr or '127.0.0.1',
        **analysis
    }
    
    ticket_id = database.add_complaint(ticket_payload)
    ticket_payload['id'] = ticket_id

    return jsonify(ticket_payload), 200

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    limit = int(request.args.get('limit', 50))
    category = request.args.get('category', None)
    priority = request.args.get('priority', None)
    status = request.args.get('status', None)
    
    complaints = database.get_complaints(limit=limit, category=category, priority=priority, status=status)
    return jsonify(complaints), 200

@app.route('/api/complaints/<int:ticket_id>', methods=['GET'])
def get_complaint(ticket_id):
    ticket = database.get_complaint_by_id(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    return jsonify(ticket), 200

@app.route('/api/tickets/<int:ticket_id>/status', methods=['POST'])
def update_status(ticket_id):
    data = request.json or {}
    new_status = data.get('status', 'IN_PROGRESS')
    notes = data.get('notes', '')
    
    success = database.update_ticket_status(ticket_id, new_status, notes)
    if not success:
        return jsonify({'error': 'Failed to update ticket'}), 400
    
    return jsonify({'success': True, 'ticket_id': ticket_id, 'status': new_status}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = database.get_stats()
    stats['active_categories'] = CATEGORIES
    return jsonify(stats), 200

@app.route('/api/departments', methods=['GET'])
def get_departments():
    depts = database.get_departments()
    return jsonify(depts), 200

@app.route('/api/audit', methods=['GET'])
def get_audit():
    limit = int(request.args.get('limit', 25))
    logs = database.get_audit_logs(limit=limit)
    return jsonify(logs), 200

@app.route('/api/model/info', methods=['GET'])
def model_info():
    return jsonify(model_metadata), 200

@app.route('/api/export/report', methods=['GET'])
def export_report():
    stats = database.get_stats()
    depts = database.get_departments()
    recent_tickets = database.get_complaints(limit=100)
    
    report = {
        'report_title': 'Executive Customer Complaint & SLA Performance Dossier',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'system_kpis': stats,
        'department_load': depts,
        'model_diagnostics': {
            'category_accuracy': model_metadata.get('category_model', {}).get('accuracy'),
            'priority_accuracy': model_metadata.get('priority_model', {}).get('accuracy'),
            'vocab_size': model_metadata.get('vocab_size')
        },
        'tickets_sample': recent_tickets[:15]
    }
    return jsonify(report), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5022))
    print(f"[INFO] Launching PROJECT-022 Server on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
