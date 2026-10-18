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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
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
        return jsonify({'status': 'success', 'data': result})
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
    return jsonify({
        'status': 'ok',
        'service': 'Multilevel RCNN with Attention Mechanism Phishing Detection',
        'port': 5002,
        'proposed_architecture': 'Improved Recurrent Convolutional Neural Network (RCNN) + Multilevel Vectors (Word + Character) + Attention Mechanism',
        'dataset_evaluation': 'Unbalanced dataset with realistic phishing-to-legitimate ratios'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"===============================================================")
    print(f" Multilevel RCNN Phishing Server starting on http://localhost:{port}")
    print(f"===============================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
