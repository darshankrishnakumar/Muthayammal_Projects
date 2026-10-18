import sys
import os
import json
import numpy as np
import pandas as pd
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
import shap
import time
from datetime import datetime
import random
from flask import Flask, request, jsonify, render_template, redirect, url_for
import base64
import io
import sklearn.tree._tree as _tree

from database import init_db, save_prediction, get_recent_predictions, get_all_predictions, get_prediction_stats
from seed_db import seed_database_if_empty

# --- Compatibility Shims for Legacy Models ---
import pandas.core.indexes.base as _pbase
if not hasattr(_pbase, 'Int64Index'):
    _pbase.Int64Index = pd.Index
if not hasattr(_pbase, 'Float64Index'):
    _pbase.Float64Index = pd.Index
sys.modules['pandas.core.indexes.numeric'] = _pbase

_dummy = _tree.Tree(1, np.array([1], dtype=np.intp), 1)
_target_dtype = _dummy.__getstate__()['nodes'].dtype

class _PatchedTree(_tree.Tree):
    def __setstate__(self, state):
        if 'nodes' in state and 'missing_go_to_left' not in state['nodes'].dtype.names:
            old_nodes = state['nodes']
            new_nodes = np.zeros(old_nodes.shape, dtype=_target_dtype)
            for name in old_nodes.dtype.names:
                new_nodes[name] = old_nodes[name]
            state['nodes'] = new_nodes
        super().__setstate__(state)

class _CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'sklearn.tree._tree' and name == 'Tree':
            return _PatchedTree
        return super().find_class(module, name)

# --- Flask App Initialization ---
app = Flask(__name__)

@app.template_filter('number_format')
def number_format_filter(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

# --- Load Trained Models ---
with open('model.pkl', 'rb') as f:
    model = _CustomUnpickler(f).load()

model.estimator = getattr(model, 'base_estimator_', None) or model.estimators_[0]
if not hasattr(model, 'monotonic_cst'):
    model.monotonic_cst = None
for est in model.estimators_:
    if not hasattr(est, 'monotonic_cst'):
        est.monotonic_cst = None

explainer = shap.TreeExplainer(model)

survmodel = pickle.load(open('survivemodel.pkl', 'rb'))

def _predict_cumulative_hazard(self, feats):
    xb = np.dot(feats, self.hazards_.values)
    partial_hazard = np.exp(xb)[0]
    df = self.baseline_cumulative_hazard_.copy() * partial_hazard
    df.columns = [0]
    return df

def _predict_survival_function(self, feats):
    ch = self.predict_cumulative_hazard(feats)
    sf = np.exp(-ch)
    return sf

survmodel.predict_cumulative_hazard = _predict_cumulative_hazard.__get__(survmodel)
survmodel.predict_survival_function = _predict_survival_function.__get__(survmodel)

# --- Initialize & Seed Database ---
init_db()
seed_database_if_empty(model, survmodel, sample_size=15)

# --- Load Model Metrics ---
METRICS_PATH = os.path.join(os.path.dirname(__file__), 'model_evaluation_metrics.json')
def get_metrics_data():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            return json.load(f)
    return {
        'total_dataset_records': 7043,
        'train_records': 5634,
        'test_records': 1409,
        'test': {'accuracy': 0.7658, 'precision': 0.5435, 'recall': 0.7353, 'f1': 0.6250, 'roc_auc': 0.8388,
                 'confusion_matrix': {'tn': 804, 'fp': 231, 'fn': 99, 'tp': 275}},
        'train': {'accuracy': 0.7994, 'precision': 0.5870, 'recall': 0.8234, 'f1': 0.6854, 'roc_auc': 0.8631,
                  'confusion_matrix': {'tn': 3273, 'fp': 866, 'fn': 264, 'tp': 1231}},
        'feature_names': [],
        'feature_importances': []
    }

# --- Helper: Generate Risk Gauge Chart ---
def degree_range(n):
    start = np.linspace(0, 180, n + 1, endpoint=True)[0:-1]
    end = np.linspace(0, 180, n + 1, endpoint=True)[1::]
    mid_points = start + ((end - start) / 2.)
    return np.c_[start, end], mid_points

def rot_text(ang):
    return np.degrees(np.radians(ang) - np.radians(90))

def generate_gauge_plot(probability):
    gauge_img = io.BytesIO()
    fig, ax = plt.subplots(figsize=(6, 4))

    labels = ['EXTREME', 'HIGH', 'MEDIUM', 'LOW']
    colors = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981']
    ang_range, mid_points = degree_range(4)

    patches = []
    for ang, c in zip(ang_range, colors):
        patches.append(Wedge((0., 0.), 0.4, *ang, facecolor='w', lw=2))
        patches.append(Wedge((0., 0.), 0.4, *ang, width=0.10, facecolor=c, lw=2, alpha=0.6))

    for p in patches:
        ax.add_patch(p)

    for mid, lab in zip(mid_points, labels):
        ax.text(0.35 * np.cos(np.radians(mid)), 0.35 * np.sin(np.radians(mid)), lab,
                horizontalalignment='center', verticalalignment='center', fontsize=11,
                fontweight='bold', rotation=rot_text(mid), color='#1E293B')

    r = Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor='w', lw=1.5, edgecolor='#E2E8F0')
    ax.add_patch(r)
    ax.text(0, -0.05, f'Churn Probability: {probability:.1%}', horizontalalignment='center',
            verticalalignment='center', fontsize=14, fontweight='bold', color='#0F172A')

    pos = (1 - probability) * 180
    ax.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)),
             width=0.03, head_width=0.08, head_length=0.08, fc='#0F172A', ec='#0F172A')
    ax.add_patch(Circle((0, 0), radius=0.02, facecolor='#0F172A'))
    ax.add_patch(Circle((0, 0), radius=0.01, facecolor='w', zorder=11))

    ax.set_frame_on(False)
    ax.axes.set_xticks([])
    ax.axes.set_yticks([])
    ax.axis('equal')
    plt.tight_layout()
    plt.savefig(gauge_img, format='png', bbox_inches='tight')
    plt.close(fig)
    gauge_img.seek(0)
    return base64.b64encode(gauge_img.getvalue()).decode()

# --- Helper: Generate Retention Action ---
def get_retention_action(prob, tenure, contract, monthly):
    if prob >= 0.60:
        if contract == 'Month-to-Month':
            return "High churn probability detected. Subscriber is on a flexible month-to-month plan. Recommended action: Proactively reach out with a dedicated customer loyalty offer, address any recent service complaints, and propose an annual discounted commitment to secure retention."
        else:
            return "High churn probability detected. Customer indicates severe dissatisfaction or price sensitivity. Recommended action: Assign a senior account representative to conduct an account review, evaluate service reliability, and offer tailored value-added service bundles."
    elif prob >= 0.35:
        if tenure < 12:
            return "Moderate retention risk identified for a relatively new subscriber. Recommended action: Send personalized onboarding check-ins, verify digital security and backup setup, and provide customer support assistance."
        else:
            return "Moderate retention risk identified. Subscriber demonstrates steady usage but shows indicators of plan fatigue. Recommended action: Present upgrade incentives or seasonal loyalty discounts before contract expiration."
    else:
        return "Low churn probability. Subscriber exhibits strong loyalty and stable usage patterns. Recommended action: Maintain standard quality engagement, offer referral reward programs, and include in periodic satisfaction feedback surveys."

# ==================== ROUTES ====================

@app.route('/')
def home():
    # Dataset benchmarks + live records
    db_stats = get_prediction_stats()
    metrics = get_metrics_data()

    # Total customers analysed (7,043 benchmark records + additional predictions)
    total_analyzed = metrics.get('total_dataset_records', 7043) + max(0, db_stats['total'] - 15)
    churn_count = int(round(total_analyzed * 0.2654))
    stay_count = total_analyzed - churn_count
    churn_rate = 26.54

    stats = {
        'total_analyzed': total_analyzed,
        'churn_count': churn_count,
        'stay_count': stay_count,
        'churn_rate': churn_rate
    }

    recent_predictions = get_recent_predictions(limit=10)
    return render_template('index.html', active_page='dashboard', stats=stats, recent_predictions=recent_predictions)

@app.route('/predict-page')
def predict_page():
    return render_template('predict.html', active_page='predict', has_prediction=False, form_data={})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        gender = int(request.form.get("gender", 0))
        SeniorCitizen = 1 if 'SeniorCitizen' in request.form else 0
        Partner = 1 if 'Partner' in request.form else 0
        Dependents = 1 if 'Dependents' in request.form else 0
        PaperlessBilling = 1 if 'PaperlessBilling' in request.form else 0

        MonthlyCharges = float(request.form.get("MonthlyCharges", 65.0))
        Tenure = int(request.form.get("Tenure", 12))
        TotalCharges = MonthlyCharges * Tenure

        PhoneService = 1 if 'PhoneService' in request.form else 0
        MultipleLines = 1 if ('MultipleLines' in request.form and PhoneService == 1) else 0

        InternetService_val = int(request.form.get("InternetService", 0))
        InternetService_Fiberoptic = 1 if InternetService_val == 2 else 0
        InternetService_No = 1 if InternetService_val == 0 else 0

        OnlineSecurity = 1 if ('OnlineSecurity' in request.form and InternetService_No == 0) else 0
        OnlineBackup = 1 if ('OnlineBackup' in request.form and InternetService_No == 0) else 0
        DeviceProtection = 1 if ('DeviceProtection' in request.form and InternetService_No == 0) else 0
        TechSupport = 1 if ('TechSupport' in request.form and InternetService_No == 0) else 0
        StreamingTV = 1 if ('StreamingTV' in request.form and InternetService_No == 0) else 0
        StreamingMovies = 1 if ('StreamingMovies' in request.form and InternetService_No == 0) else 0

        Contract_val = int(request.form.get("Contract", 0))
        Contract_Oneyear = 1 if Contract_val == 1 else 0
        Contract_Twoyear = 1 if Contract_val == 2 else 0

        PaymentMethod_val = int(request.form.get("PaymentMethod", 0))
        PaymentMethod_CreditCard = 1 if PaymentMethod_val == 1 else 0
        PaymentMethod_ElectronicCheck = 1 if PaymentMethod_val == 2 else 0
        PaymentMethod_MailedCheck = 1 if PaymentMethod_val == 3 else 0

        features = [
            gender, SeniorCitizen, Partner, Dependents, Tenure, PhoneService, MultipleLines,
            OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies,
            PaperlessBilling, MonthlyCharges, TotalCharges, InternetService_Fiberoptic, InternetService_No,
            Contract_Oneyear, Contract_Twoyear, PaymentMethod_CreditCard, PaymentMethod_ElectronicCheck,
            PaymentMethod_MailedCheck
        ]

        columns = [
            'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 'PhoneService', 'MultipleLines',
            'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
            'PaperlessBilling', 'MonthlyCharges', 'TotalCharges', 'InternetService_Fiber optic', 'InternetService_No',
            'Contract_One year', 'Contract_Two year', 'PaymentMethod_Credit card (automatic)',
            'PaymentMethod_Electronic check', 'PaymentMethod_Mailed check'
        ]

        final_features = [np.array(features)]
        prediction_proba = model.predict_proba(final_features)
        output = float(prediction_proba[0, 1])

        prediction_status = 'Churn' if output >= 0.50 else 'No Churn'
        if output >= 0.60:
            risk_level = 'High'
        elif output >= 0.35:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        contract_name = 'Month-to-Month' if Contract_val == 0 else ('One-Year' if Contract_val == 1 else 'Two-Year')
        action_recommendation = get_retention_action(output, Tenure, contract_name, MonthlyCharges)

        # 1. SHAP Values Plot
        shap_values = explainer.shap_values(np.array(final_features))
        shap_img = io.BytesIO()
        if isinstance(shap_values, list):
            s1 = shap_values[1]
        elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
            s1 = shap_values[0, :, 1]
        else:
            s1 = shap_values[0]

        ev = explainer.expected_value
        base_val = ev[1] if isinstance(ev, (list, np.ndarray)) and len(ev) > 1 else (ev[0] if isinstance(ev, (list, np.ndarray)) else ev)

        plt.figure(figsize=(10, 3.5))
        shap.force_plot(base_val, s1, columns, matplotlib=True, show=False)
        plt.savefig(shap_img, bbox_inches="tight", format='png')
        plt.close()
        shap_img.seek(0)
        shap_url = base64.b64encode(shap_img.getvalue()).decode()

        # 2. Survival & Cumulative Hazard Analysis
        surv_feats = np.array([
            gender, SeniorCitizen, Partner, Dependents, PhoneService, MultipleLines, OnlineSecurity, OnlineBackup,
            DeviceProtection, TechSupport, StreamingTV, StreamingMovies, PaperlessBilling, MonthlyCharges, TotalCharges,
            InternetService_Fiberoptic, InternetService_No, Contract_Oneyear, Contract_Twoyear,
            PaymentMethod_CreditCard, PaymentMethod_ElectronicCheck, PaymentMethod_MailedCheck
        ]).reshape(1, -1)

        hazard_img = io.BytesIO()
        fig, ax = plt.subplots(figsize=(6, 4))
        survmodel.predict_cumulative_hazard(surv_feats).plot(ax=ax, color='#DC2626', lw=2)
        plt.axvline(x=Tenure, color='#2563EB', linestyle='--', lw=2)
        plt.legend(labels=['Cumulative Hazard', 'Current Position'])
        ax.set_xlabel('Tenure (Months)', size=10)
        ax.set_ylabel('Cumulative Hazard', size=10)
        ax.set_title('Cumulative Hazard Over Time', fontsize=11, fontweight='bold', color='#0F172A')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(hazard_img, format='png')
        plt.close(fig)
        hazard_img.seek(0)
        hazard_url = base64.b64encode(hazard_img.getvalue()).decode()

        surv_img = io.BytesIO()
        fig, ax = plt.subplots(figsize=(6, 4))
        survmodel.predict_survival_function(surv_feats).plot(ax=ax, color='#16A34A', lw=2)
        plt.axvline(x=Tenure, color='#2563EB', linestyle='--', lw=2)
        plt.legend(labels=['Survival Probability', 'Current Position'])
        ax.set_xlabel('Tenure (Months)', size=10)
        ax.set_ylabel('Survival Probability', size=10)
        ax.set_title('Subscriber Survival Probability Over Time', fontsize=11, fontweight='bold', color='#0F172A')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(surv_img, format='png')
        plt.close(fig)
        surv_img.seek(0)
        surv_url = base64.b64encode(surv_img.getvalue()).decode()

        # 3. CLTV calculation
        try:
            life = survmodel.predict_survival_function(surv_feats).reset_index()
            life.columns = ['Tenure', 'Probability']
            max_life = life.Tenure[life.Probability > 0.1].max()
            cltv = round(float(max_life * MonthlyCharges), 2)
        except Exception:
            cltv = round(float(24 * MonthlyCharges), 2)

        # 4. Needle Gauge
        gauge_url = generate_gauge_plot(output)

        # 5. Save to Persistent Database
        cust_id = f"CUST-{random.randint(10000, 99999)}"
        record = {
            'customer_id': cust_id,
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gender': 'Female' if gender == 1 else 'Male',
            'senior_citizen': SeniorCitizen,
            'partner': Partner,
            'dependents': Dependents,
            'tenure': Tenure,
            'phone_service': PhoneService,
            'multiple_lines': MultipleLines,
            'internet_service': 'Fiber optic' if InternetService_val == 2 else ('DSL' if InternetService_val == 1 else 'No'),
            'online_security': OnlineSecurity,
            'online_backup': OnlineBackup,
            'device_protection': DeviceProtection,
            'tech_support': TechSupport,
            'streaming_tv': StreamingTV,
            'streaming_movies': StreamingMovies,
            'contract': contract_name,
            'paperless_billing': PaperlessBilling,
            'payment_method': 'Electronic check' if PaymentMethod_val == 2 else ('Credit card' if PaymentMethod_val == 1 else ('Mailed check' if PaymentMethod_val == 3 else 'Bank transfer')),
            'monthly_charges': MonthlyCharges,
            'total_charges': TotalCharges,
            'prediction_status': prediction_status,
            'churn_probability': round(output, 4),
            'risk_level': risk_level,
            'cltv': cltv,
            'action_suggested': action_recommendation
        }
        save_prediction(record)

        return render_template(
            'predict.html',
            active_page='predict',
            has_prediction=True,
            prediction_status=prediction_status,
            prob_value=output,
            risk_level=risk_level,
            cltv_value=cltv,
            action_recommendation=action_recommendation,
            url_1=gauge_url,
            url_2=shap_url,
            url_3=hazard_url,
            url_4=surv_url,
            form_data=request.form
        )

    except Exception as e:
        return render_template(
            'predict.html',
            active_page='predict',
            has_prediction=False,
            error_message=f"Prediction error: {str(e)}",
            form_data=request.form
        )

@app.route('/model-performance')
def performance_page():
    metrics = get_metrics_data()
    return render_template('performance.html', active_page='performance', metrics=metrics)

@app.route('/history')
def history_page():
    all_predictions = get_all_predictions()
    return render_template('history.html', active_page='history', all_predictions=all_predictions)

# --- REST API Endpoints ---
@app.route('/api/metrics')
def api_metrics():
    return jsonify(get_metrics_data())

@app.route('/api/history')
def api_history():
    return jsonify(get_all_predictions())

@app.route('/api/stats')
def api_stats():
    return jsonify(get_prediction_stats())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
