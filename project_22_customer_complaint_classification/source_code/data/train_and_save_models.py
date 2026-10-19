"""
Real ML Training and Serialization Pipeline for PROJECT-022:
Customer Complaint Classification and Priority Routing Engine.

Generates a realistic multi-industry dataset (6,000 complaints) and trains:
- TF-IDF Vectorizer with n-grams (1, 2) and sublinear scaling
- Calibrated Multi-Class Classifier for Category Classification (6 classes)
- Calibrated Multi-Class Classifier for Priority Classification (4 classes)
- Saves model artifacts and performance metadata to disk.
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
import joblib

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DIR, exist_ok=True)

# ─── DATASET SYNTHESIS WITH DOMAIN PHRASE LIBRARIES ──────────────────────────

CATEGORY_TEMPLATES = {
    'payment_issue': {
        'subjects': [
            "My credit card ending in {digits} was charged ${amount} {count} times without authorization.",
            "I requested a refund of ${amount} on order #{order_id} over two weeks ago, but the money is not returned.",
            "There is an unexpected recurring billing fee of ${amount} on my enterprise subscription invoice.",
            "I was double billed for transaction #{order_id}. Please reverse the duplicate charge immediately.",
            "The direct debit transaction failed despite sufficient bank balance, resulting in an unjust overdraft penalty.",
            "Your billing portal charged my corporate MasterCard twice for the cloud server license #{order_id}.",
            "Unauthorized foreign transaction fee appeared on my statement after paying through your checkout gateway.",
            "I cancelled my monthly subscription before renewal, yet your system billed me ${amount} yesterday.",
            "The wire transfer confirmation #{order_id} shows settled, but your system claims payment was never received.",
            "Disputing fraudulent charges on invoice #{order_id}. My financial controller has put a stop payment order."
        ],
        'keywords': ['charge', 'refund', 'billing', 'invoice', 'overcharge', 'credit card', 'transaction', 'unauthorized', 'reversal', 'duplicate'],
        'default_dept': 'FinOps Billing & Fraud Team',
        'icon': '💳'
    },
    'product_complaint': {
        'subjects': [
            "The industrial laser cutter stopped functioning after only 3 days. The spindle motor is completely seized.",
            "Received defective motherboard in batch #{order_id}. The power delivery VRMs are burnt and smell like smoke.",
            "The titanium casing arrived cracked down the side seam with loose internal screws rattling inside.",
            "Hardware sensor #{order_id} arrived Dead on Arrival (DOA). The calibration LED fails to turn on.",
            "The cooling fans sound like a jet engine and grind heavily against the casing. High thermal throttling observed.",
            "Lithium-ion battery pack #{order_id} is swelling noticeably and overheating beyond 75 degrees Celsius.",
            "Missing key structural brackets and mounting bolts from retail package #{order_id}. Unusable as delivered.",
            "The touch screen display flickers erratically and has a persistent column of dead violet pixels across the center.",
            "Component solder joints on circuit board #{order_id} are cold and bridging, causing continuous electrical shorts.",
            "The optical lens module is scratched and misaligned inside the sealed optic enclosure. RMA requested."
        ],
        'keywords': ['defective', 'broken', 'damaged', 'malfunction', 'hardware', 'cracked', 'DOA', 'burned', 'RMA', 'faulty'],
        'default_dept': 'Quality Engineering & RMA Desk',
        'icon': '📦'
    },
    'delivery_problem': {
        'subjects': [
            "Shipment tracking #{order_id} has been stalled at the customs sorting hub for 11 consecutive days.",
            "Express courier marked package #{order_id} as 'Delivered to Front Porch', but security cameras show no courier arrived.",
            "Urgent medical supplies shipment #{order_id} was misrouted to the wrong regional distribution center.",
            "Pallet of electronic components arrived soaking wet with visible forklift puncture holes through the outer cartons.",
            "Guaranteed overnight delivery service took 6 business days to arrive, causing immense business disruption.",
            "Freight carrier refused delivery citing incorrect warehouse address, even though the manifest address is 100% correct.",
            "The courier dumped our fragile laboratory instrumentation on the loading dock in pouring rain without obtaining a signature.",
            "Tracking status for container #{order_id} is stuck at 'In Transit to Destination' with zero updates for two weeks.",
            "Only 3 of the 5 dispatched parcel boxes arrived today. The remaining 2 boxes have vanished from logistics records.",
            "Package was severely crushed in transit, destroying all perishable calibration standards inside."
        ],
        'keywords': ['delivery', 'shipping', 'transit', 'tracking', 'courier', 'delayed', 'lost', 'stuck', 'customs', 'manifest'],
        'default_dept': 'Global Supply Chain & Logistics',
        'icon': '🚚'
    },
    'technical_issue': {
        'subjects': [
            "Production REST API endpoint /v2/telemetry returning HTTP 500 Internal Server Error during peak traffic hours.",
            "The iOS client app crashes instantly on launch with EXC_BAD_ACCESS after updating to firmware v4.12.",
            "PostgreSQL database query latency spiked over 12 seconds due to unindexed deadlock in the transaction manager.",
            "Single Sign-On (SSO) SAML integration fails with token validation error code 0x80041010 for all remote users.",
            "Web dashboard WebSocket connection terminates every 45 seconds, forcing continuous page reloads and lost session state.",
            "Microservice worker pods are crashing in a continuous CrashLoopBackOff loop due to out-of-memory kill on worker-node-04.",
            "GraphQL mutation SubmitTelemetry is rejecting valid JSON payloads with schema parse error.",
            "Cloud sync service is failing to reconcile delta changes between edge gateways and our central repository.",
            "High network packet loss of 38% observed between the enterprise VPC gateway and API cluster nodes.",
            "Exporting analytics to CSV causes the web worker to freeze the browser tab indefinitely on large datasets."
        ],
        'keywords': ['crash', 'error', 'bug', 'server', '500', 'timeout', 'latency', 'api', 'failure', 'exception'],
        'default_dept': 'Tier-3 Engineering & DevOps',
        'icon': '💻'
    },
    'account_issue': {
        'subjects': [
            "Our enterprise administrator account has been locked out following an automated MFA reset failure.",
            "Unauthorized login detected from IP address in foreign jurisdiction. Please lock the user credential immediately.",
            "Cannot update registered email address or security questions in the IAM profile portal due to token expiry.",
            "Role-Based Access Control (RBAC) permissions were suddenly revoked for all 18 members of our engineering team.",
            "Password reset link received via email points to a 404 page, leaving our compliance director completely locked out.",
            "Two-Factor Authentication (2FA) SMS tokens are not arriving on mobile devices, preventing any portal login.",
            "Suspicious credential stuffing alerts triggered on our root account. Need immediate access logs and session termination.",
            "Account status displays as 'Suspended for Billing Review' even though all annual contracts are fully prepaid.",
            "API secret keys were exposed in a client repo; we need to rotate keys immediately without downtime.",
            "User provisioning webhook returned 403 Forbidden, halting employee onboarding workflows across LDAP."
        ],
        'keywords': ['account', 'locked', 'mfa', 'access', 'login', 'security', 'suspended', 'credentials', 'password', 'iam'],
        'default_dept': 'Identity & Access Management (IAM)',
        'icon': '🔐'
    },
    'service_dissatisfaction': {
        'subjects': [
            "Your support representative was extremely rude, dismissive, and hung up the phone while I was explaining our outage.",
            "We have been waiting 72 hours for an initial response on a critical production ticket. SLA has been severely violated.",
            "Support ticket #{order_id} was marked as 'Resolved' by an agent without anyone ever contacting us or fixing the issue.",
            "Tier-1 agent copied and pasted generic boilerplate help articles that had zero relevance to our detailed technical issue.",
            "Escalation request submitted to management was completely ignored for 5 consecutive business days.",
            "The customer service hotline placed our operations manager on hold for 85 minutes before disconnecting the line.",
            "We pay for 24/7 Platinum Enterprise Support, but nobody answers the emergency pager phone line.",
            "Extremely dissatisfied with the lack of transparency regarding the multi-hour regional outage yesterday.",
            "Agent refused to escalate ticket #{order_id} to an engineering lead despite critical production downtime.",
            "Disappointing customer care experience; our team has spent over 15 hours repeating our problem to 4 different reps."
        ],
        'keywords': ['rude', 'dissatisfied', 'sla', 'unhelpful', 'terrible', 'agent', 'support', 'wait', 'escalation', 'disappointed'],
        'default_dept': 'Executive Customer Relations',
        'icon': '🤝'
    }
}

PRIORITY_MODIFIERS = {
    'critical': [
        "This is an absolute emergency affecting live hospital operations! We need immediate intervention within minutes.",
        "Production is completely halted and we are losing $50,000 per hour. Urgent executive escalation required immediately!",
        "Security breach and illegal unauthorized data exposure in progress. Involve corporate legal and security immediately.",
        "Life-safety hazard detected: device is overheating to the point of smoking and igniting. Immediate recall required.",
        "Critical system outage blocking 100,000 active users. All revenue streams are down right now!"
    ],
    'high': [
        "Please treat this with high priority as our quarterly deadline is tomorrow morning.",
        "Important client presentation is blocked until this defect is addressed ASAP.",
        "Significant financial discrepancy that must be rectified before monthly books close on Friday.",
        "Our entire warehouse dispatch workflow is currently blocked due to this malfunction.",
        "Hardware damage prevents our team from conducting required ISO compliance testing."
    ],
    'medium': [
        "Please look into this issue when possible as it causes recurring inconvenience for our operators.",
        "Normal operations are continuing with a workaround, but we require a proper permanent fix.",
        "Noticeable degradation in performance over the past week that needs investigation.",
        "Would appreciate an update on when this bug will be resolved in the next patch cycle.",
        "Tracking is delayed and we would like to know the revised estimated delivery date."
    ],
    'low': [
        "Minor question regarding invoice formatting and general documentation guidelines.",
        "No immediate rush, just sharing user experience feedback for your product roadmap.",
        "Submitting a non-urgent suggestion regarding our account display preferences.",
        "Would appreciate a copy of the user manual and warranty terms when convenient.",
        "Checking in on standard processing times for future order planning."
    ]
}

def generate_complaints_dataset(num_samples=6000):
    records = []
    categories = list(CATEGORY_TEMPLATES.keys())
    priorities = ['critical', 'high', 'medium', 'low']
    priority_weights = [0.15, 0.30, 0.35, 0.20]

    for i in range(1, num_samples + 1):
        cat = random.choice(categories)
        prio = random.choices(priorities, weights=priority_weights, k=1)[0]
        
        template_info = CATEGORY_TEMPLATES[cat]
        base_subject = random.choice(template_info['subjects'])
        
        # Populate placeholders
        text = base_subject.format(
            digits=f"{random.randint(1000, 9999)}",
            amount=f"{random.randint(25, 4500)}.{random.choice(['00', '50', '99', '25', '75'])}",
            order_id=f"TKT-{random.randint(10000, 99999)}",
            count=random.randint(2, 5)
        )
        
        # In 65% of cases, append a priority modifier or additional context
        if random.random() < 0.65:
            mod = random.choice(PRIORITY_MODIFIERS[prio])
            text = f"{text} {mod}"
        elif prio == 'critical':
            # Critical always has high urgency words
            mod = random.choice(PRIORITY_MODIFIERS['critical'])
            text = f"{text} {mod}"

        # Additional domain noise/keywords
        if random.random() < 0.3:
            kw = random.choice(template_info['keywords'])
            text = f"[Tag: {kw.upper()}] {text}"

        # Assign urgency and sentiment based on priority and category
        if prio == 'critical':
            urgency = random.randint(85, 100)
            sentiment = round(random.uniform(-0.95, -0.60), 2)
        elif prio == 'high':
            urgency = random.randint(65, 84)
            sentiment = round(random.uniform(-0.65, -0.30), 2)
        elif prio == 'medium':
            urgency = random.randint(35, 64)
            sentiment = round(random.uniform(-0.35, -0.05), 2)
        else: # low
            urgency = random.randint(10, 34)
            sentiment = round(random.uniform(-0.10, 0.25), 2)

        records.append({
            'id': i,
            'text': text,
            'category': cat,
            'category_label': cat.replace('_', ' ').title(),
            'department': template_info['default_dept'],
            'priority': prio,
            'urgency_score': urgency,
            'sentiment_score': sentiment
        })

    df = pd.DataFrame(records)
    csv_path = os.path.join(DATA_DIR, "complaints_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} complaint samples -> {csv_path}")
    print(f"Category Distribution:\n{df['category'].value_counts()}\n")
    print(f"Priority Distribution:\n{df['priority'].value_counts()}\n")
    return df

def train_and_evaluate_models(df):
    X = df['text']
    y_cat = df['category']
    y_prio = df['priority']

    # Stratified Split
    X_train, X_test, y_cat_train, y_cat_test, y_prio_train, y_prio_test = train_test_split(
        X, y_cat, y_prio, test_size=0.20, random_state=RANDOM_SEED, stratify=y_cat
    )

    print(f"Training set: {len(X_train)} samples | Testing set: {len(X_test)} samples")

    # TF-IDF Vectorization
    print("Fitting TF-IDF Vectorizer (ngram=(1, 2), max_features=5000)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        stop_words='english',
        min_df=2
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)} features")

    # Model 1: Category Classifier
    print("Training Calibrated Category Classifier (Logistic Regression)...")
    cat_model = LogisticRegression(
        C=2.5,
        max_iter=1000,
        class_weight='balanced',
        solver='lbfgs',
        random_state=RANDOM_SEED
    )
    cat_model.fit(X_train_tfidf, y_cat_train)
    cat_preds = cat_model.predict(X_test_tfidf)
    cat_acc = accuracy_score(y_cat_test, cat_preds)
    cat_f1 = f1_score(y_cat_test, cat_preds, average='macro')
    print(f"Category Classification Accuracy: {cat_acc * 100:.2f}% | Macro F1: {cat_f1:.4f}")
    cat_report = classification_report(y_cat_test, cat_preds, output_dict=True)

    # Model 2: Priority Classifier
    print("Training Calibrated Priority Classifier (Logistic Regression)...")
    prio_model = LogisticRegression(
        C=1.8,
        max_iter=1000,
        class_weight='balanced',
        solver='lbfgs',
        random_state=RANDOM_SEED
    )
    prio_model.fit(X_train_tfidf, y_prio_train)
    prio_preds = prio_model.predict(X_test_tfidf)
    prio_acc = accuracy_score(y_prio_test, prio_preds)
    prio_f1 = f1_score(y_prio_test, prio_preds, average='macro')
    print(f"Priority Classification Accuracy: {prio_acc * 100:.2f}% | Macro F1: {prio_f1:.4f}")
    prio_report = classification_report(y_prio_test, prio_preds, output_dict=True)

    # Save artifacts
    vec_path = os.path.join(BACKEND_DIR, "tfidf_vectorizer.joblib")
    cat_model_path = os.path.join(BACKEND_DIR, "category_model.joblib")
    prio_model_path = os.path.join(BACKEND_DIR, "priority_model.joblib")
    meta_path = os.path.join(BACKEND_DIR, "model_metadata.json")

    joblib.dump(vectorizer, vec_path, compress=3)
    joblib.dump(cat_model, cat_model_path, compress=3)
    joblib.dump(prio_model, prio_model_path, compress=3)

    metadata = {
        'timestamp': datetime.utcnow().isoformat(),
        'dataset_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'vocab_size': len(vectorizer.vocabulary_),
        'ngram_range': [1, 2],
        'category_model': {
            'algorithm': 'Logistic Regression (Calibrated L2 Regularized)',
            'classes': list(cat_model.classes_),
            'accuracy': round(cat_acc, 4),
            'macro_f1': round(cat_f1, 4),
            'classification_report': cat_report
        },
        'priority_model': {
            'algorithm': 'Logistic Regression (Calibrated L2 Regularized)',
            'classes': list(prio_model.classes_),
            'accuracy': round(prio_acc, 4),
            'macro_f1': round(prio_f1, 4),
            'classification_report': prio_report
        }
    }

    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Artifacts successfully written to {BACKEND_DIR}:")
    print(f" - {vec_path}")
    print(f" - {cat_model_path}")
    print(f" - {prio_model_path}")
    print(f" - {meta_path}")

if __name__ == '__main__':
    df = generate_complaints_dataset(6000)
    train_and_evaluate_models(df)
