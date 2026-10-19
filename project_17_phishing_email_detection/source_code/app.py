import os
import sys

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from phishing_engine import PhishingEngine

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize the phishing engine with RCNN + Multilevel Attention
print("Initializing RCNN Multilevel Attention Deep Learning Engine...")
engine = PhishingEngine()
print("RCNN Multilevel Attention Engine Ready.")

SAMPLE_EMAILS = [
    {
        "id": "sample-phish-rcnn-1",
        "title": "Bank Account Impersonation (Spoofed Header + Body)",
        "category": "Phishing (Header Spoofing & Credential Theft)",
        "from": "security-alert@chase-secure-verify.com",
        "subject": "URGENT: Immediate Account Suspension - Verification Required",
        "reply_to": "fraud-harvest@server-host.xyz",
        "spf_dkim": "fail (SPF check failed: IP not authorized)",
        "body": "Dear Valued Customer,\n\nOur automated fraud monitoring system detected unauthorized login attempts from an untrusted device in Moscow, Russia. Your online banking access has been restricted to prevent further financial losses.\n\nPlease verify your online banking password, routing credentials, and debit card PIN immediately within 24 hours:\nhttp://chase-secure-verify.com/login?auth=9821\n\nFailure to verify will lead to permanent account suspension."
    },
    {
        "id": "sample-phish-rcnn-2",
        "title": "Microsoft 365 Domain Typo-Squatting",
        "category": "Phishing (Char-level Obfuscation & SSO Harvesting)",
        "from": "admin@micros0ft-support365.top",
        "subject": "CRITICAL: Your Microsoft 365 Password Expires in 2 Hours",
        "reply_to": "admin@micros0ft-support365.top",
        "spf_dkim": "softfail (domain does not sign mail with DKIM)",
        "body": "Dear Employee,\n\nYour organization credentials for Microsoft 365, Teams, and Exchange Outlook are scheduled to expire today. To retain your current password and avoid service disconnection, submit your corporate credentials via the secure single sign-on portal:\n\nhttp://micros0ft-support365.top/auth/sso-update\n\nHelpdesk Support Department"
    },
    {
        "id": "sample-phish-rcnn-3",
        "title": "CEO Wire Fraud (Executive Impersonation)",
        "category": "Phishing (BEC / Financial Wire)",
        "from": "ceo-direct@executive-mail.vip",
        "subject": "Urgent wire payment instruction - strictly confidential",
        "reply_to": "offshore-wire@overseas-bank.cc",
        "spf_dkim": "none (no SPF record found for sender domain)",
        "body": "Hi,\n\nI am currently attending a closed-door acquisition meeting and cannot take calls right now. We need an urgent wire transfer of $45,000 processed today for our vendor retainer.\n\nPlease route the wire immediately to the overseas account details attached. Reply with the confirmation number as soon as the transaction is queued."
    },
    {
        "id": "sample-safe-rcnn-1",
        "title": "Authentic Corporate Sprint Standup",
        "category": "Legitimate (Internal Team)",
        "from": "alex.chen@techcorp.internal",
        "subject": "Engineering Team: Daily Sync & Sprint Review at 2:00 PM",
        "reply_to": "alex.chen@techcorp.internal",
        "spf_dkim": "pass (DKIM verified: techcorp.internal)",
        "body": "Hi everyone,\n\nQuick reminder that our daily sprint sync is scheduled for today at 2:00 PM in Conference Room B and via Google Meet. Please make sure your Jira backlog tasks are updated before the call.\n\nAgenda:\n1. Sprint 42 blocker review\n2. PyTorch RCNN model training latency\n3. Staging rollout checklist\n\nBest,\nAlex"
    },
    {
        "id": "sample-safe-rcnn-2",
        "title": "Verified E-Commerce Shipment",
        "category": "Legitimate (Automated Notification)",
        "from": "order-update@fedex.com",
        "subject": "FedEx Tracking Update: Package #91823901 Scheduled for Delivery",
        "reply_to": "support@fedex.com",
        "spf_dkim": "pass (SPF verified: fedex.com IP authorized)",
        "body": "Hello,\n\nYour package containing the ergonomic keyboard has been scanned at the regional sorting facility. Delivery is scheduled for Friday by 4:30 PM.\n\nTracking Number: FX-9182390184\nNo further action or payment is required on your part. Thank you for shipping with FedEx."
    },
    {
        "id": "sample-safe-rcnn-3",
        "title": "Academic Research Manuscript Review",
        "category": "Legitimate (Scholarly Publication)",
        "from": "editor@ieee-security.org",
        "subject": "IEEE S&P: Peer Review Comments on RCNN Attention Paper",
        "reply_to": "editor@ieee-security.org",
        "spf_dkim": "pass (DKIM verified: ieee-security.org)",
        "body": "Dear Author,\n\nThank you for submitting your manuscript 'Phishing Email Detection with Multilevel RCNN and Attention Mechanism'. The reviewers praised your empirical evaluation on unbalanced datasets with realistic traffic ratios.\n\nPlease find the editorial revision requests attached for the final camera-ready copy.\n\nSincerely,\nIEEE Editorial Committee"
    }
]

import sqlite3
import time
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phishing_scans.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS email_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            from_hdr TEXT,
            reply_to_hdr TEXT,
            spf_dkim_hdr TEXT,
            subject_hdr TEXT,
            body_snippet TEXT,
            selected_model TEXT,
            is_phishing INTEGER,
            phishing_probability REAL,
            threat_level TEXT,
            risk_class TEXT,
            header_risk REAL,
            body_risk REAL,
            consensus_phish_votes INTEGER,
            latency_ms REAL
        )
    ''')
    conn.commit()

    cur.execute('SELECT COUNT(*) FROM email_scans')
    count = cur.fetchone()[0]
    if count == 0:
        seed_data = [
            ("2026-10-18 10:14:22", "security-alert@chase-secure-verify.com", "fraud-harvest@server-host.xyz", "fail", "URGENT: Immediate Account Suspension - Verification Required", "Dear Valued Customer, Our automated fraud monitoring system detected...", "rcnn_attn", 1, 98.4, "CRITICAL / PHISHING CONFIRMED", "danger", 85.0, 96.5, 9, 14.2),
            ("2026-10-18 11:30:05", "admin@micros0ft-support365.top", "admin@micros0ft-support365.top", "softfail", "CRITICAL: Your Microsoft 365 Password Expires in 2 Hours", "Dear Employee, Your organization credentials for Microsoft 365...", "rcnn_attn", 1, 95.8, "CRITICAL / PHISHING CONFIRMED", "danger", 60.0, 92.4, 9, 12.8),
            ("2026-10-18 14:05:19", "ceo-direct@executive-mail.vip", "offshore-wire@overseas-bank.cc", "none", "Urgent wire payment instruction - strictly confidential", "Hi, I am currently attending a closed-door acquisition meeting...", "ensemble", 1, 91.2, "CRITICAL / PHISHING CONFIRMED", "danger", 90.0, 88.0, 8, 18.5),
            ("2026-10-18 16:45:33", "alex.chen@techcorp.internal", "alex.chen@techcorp.internal", "pass", "Engineering Team: Daily Sync & Sprint Review at 2:00 PM", "Hi everyone, Quick reminder that our daily sprint sync is scheduled...", "rcnn_attn", 0, 1.2, "LEGITIMATE / AUTHENTICATED", "safe", 0.0, 1.8, 0, 11.5),
            ("2026-10-19 09:12:44", "order-update@fedex.com", "support@fedex.com", "pass", "FedEx Tracking Update: Package #91823901 Scheduled for Delivery", "Hello, Your package containing the ergonomic keyboard has been scanned...", "rcnn_attn", 0, 0.8, "LEGITIMATE / AUTHENTICATED", "safe", 0.0, 1.2, 0, 9.8),
            ("2026-10-19 11:25:10", "editor@ieee-security.org", "editor@ieee-security.org", "pass", "IEEE S&P: Peer Review Comments on RCNN Attention Paper", "Dear Author, Thank you for submitting your manuscript...", "rcnn_attn", 0, 1.5, "LEGITIMATE / AUTHENTICATED", "safe", 0.0, 2.1, 0, 10.4)
        ]
        cur.executemany('''
            INSERT INTO email_scans (
                timestamp, from_hdr, reply_to_hdr, spf_dkim_hdr, subject_hdr,
                body_snippet, selected_model, is_phishing, phishing_probability,
                threat_level, risk_class, header_risk, body_risk,
                consensus_phish_votes, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_data)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        t0 = time.time()
        data = request.get_json(force=True)
        from_hdr = data.get('from', '').strip()
        subject_hdr = data.get('subject', '').strip()
        reply_to_hdr = data.get('reply_to', '').strip()
        spf_dkim_hdr = data.get('spf_dkim', 'pass').strip()
        email_body = data.get('email_text', '').strip()
        selected_model = data.get('model', 'rcnn_attn')

        if not email_body and not subject_hdr:
            return jsonify({'error': 'Email content (subject or body) cannot be empty'}), 400

        result = engine.analyze_email_multilevel(
            from_hdr=from_hdr,
            subject_hdr=subject_hdr,
            reply_to_hdr=reply_to_hdr,
            spf_dkim_hdr=spf_dkim_hdr,
            email_body=email_body,
            selected_model=selected_model
        )
        latency = round((time.time() - t0) * 1000, 2)
        result['latency_ms'] = latency

        # Transactional SQLite logging
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            snippet = (email_body[:80] + '...') if len(email_body) > 80 else email_body
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute('''
                INSERT INTO email_scans (
                    timestamp, from_hdr, reply_to_hdr, spf_dkim_hdr, subject_hdr,
                    body_snippet, selected_model, is_phishing, phishing_probability,
                    threat_level, risk_class, header_risk, body_risk,
                    consensus_phish_votes, latency_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                now_str, from_hdr, reply_to_hdr, spf_dkim_hdr, subject_hdr,
                snippet, selected_model, 1 if result['is_phishing'] else 0,
                result['phishing_probability'], result['threat_level'], result['risk_class'],
                result['multilevel_breakdown']['header_risk'], result['multilevel_breakdown']['body_risk'],
                int(result['consensus'].split('/')[0]) if '/' in result['consensus'] else 0,
                latency
            ))
            scan_id = cur.lastrowid
            conn.commit()
            conn.close()
            result['scan_id'] = scan_id
        except Exception as db_err:
            print(f"Warning: Database logging failed: {db_err}")

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM email_scans ORDER BY id DESC LIMIT 50')
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify({'status': 'success', 'count': len(rows), 'history': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*), SUM(is_phishing), AVG(phishing_probability), AVG(latency_ms) FROM email_scans')
        total, phish, avg_score, avg_lat = cur.fetchone()
        conn.close()
        total = total or 0
        phish = phish or 0
        safe = total - phish
        rate = round((phish / total * 100), 1) if total > 0 else 0.0
        return jsonify({
            'status': 'success',
            'stats': {
                'total_scans': total,
                'phishing_detected': phish,
                'legitimate_verified': safe,
                'phishing_rate_pct': rate,
                'avg_threat_score': round(avg_score or 0.0, 1),
                'avg_latency_ms': round(avg_lat or 0.0, 1)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/benchmark', methods=['GET'])
def benchmark():
    return jsonify({
        'status': 'success',
        'benchmarks': engine.benchmark_data
    })

@app.route('/api/samples', methods=['GET'])
def samples():
    return jsonify({
        'status': 'success',
        'samples': SAMPLE_EMAILS
    })

@app.route('/health', methods=['GET'])
def health():
    active_port = int(os.environ.get('PORT', 5017))
    return jsonify({
        'status': 'ok',
        'service': 'Multilevel RCNN with Attention Mechanism Phishing Detection',
        'port': active_port,
        'database': 'SQLite Connected (phishing_scans.db)',
        'proposed_architecture': 'Improved Recurrent Convolutional Neural Network (RCNN) + Multilevel Vectors (Word + Character) + Attention Mechanism',
        'dataset_evaluation': 'Unbalanced dataset with realistic phishing-to-legitimate ratios'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5017))
    print(f"===============================================================")
    print(f" Multilevel RCNN Phishing Server starting on http://localhost:{port}")
    print(f"===============================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
