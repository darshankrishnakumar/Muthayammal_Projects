from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pickle
import numpy as np
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os
import database as db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_BUILD_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

app = Flask(
    __name__,
    static_folder=REACT_BUILD_DIR,
    static_url_path=''
)
CORS(app)

# Load model
MODEL_PATH = os.path.join(BASE_DIR, "heart_model.pkl")
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

# Ensure database is initialized
db.init_db()

def generate_pdf_report(prediction_result, input_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2196F3')
    )
    story.append(Paragraph("Heart Disease Risk Assessment Report", title_style))
    story.append(Spacer(1, 20))

    # Date and Time
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray
    )
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    story.append(Spacer(1, 30))

    # Prediction Result
    result_style = ParagraphStyle(
        'ResultStyle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#4CAF50') if "No Heart Disease" in str(prediction_result) else colors.HexColor('#F44336')
    )
    story.append(Paragraph("Prediction Result:", styles['Heading2']))
    story.append(Paragraph(str(prediction_result), result_style))
    story.append(Spacer(1, 30))

    # Input Data
    story.append(Paragraph("Input Parameters:", styles['Heading2']))
    
    # Convert input data to proper types safely
    if not input_data or len(input_data) < 11:
        input_data = [50, 1, 0, 120, 200, 0, 0, 150, 0, 0.0, 1]
    input_data = [float(x) for x in input_data]
    
    # Create data for the table
    cpt_labels = ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"]
    ecg_labels = ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"]
    slope_labels = ["Upsloping", "Flat", "Downsloping"]

    cpt_idx = int(input_data[2]) if 0 <= int(input_data[2]) < 4 else 0
    ecg_idx = int(input_data[6]) if 0 <= int(input_data[6]) < 3 else 0
    slope_idx = int(input_data[10]) if 0 <= int(input_data[10]) < 3 else 1

    data = [
        ["Parameter", "Value"],
        ["Age", str(int(input_data[0]))],
        ["Sex", "Male" if int(input_data[1]) == 1 else "Female"],
        ["Chest Pain Type", cpt_labels[cpt_idx]],
        ["Resting Blood Pressure", f"{int(input_data[3])} mm Hg"],
        ["Cholesterol", f"{int(input_data[4])} mg/dL"],
        ["Fasting Blood Sugar", "> 120 mg/dL" if int(input_data[5]) == 1 else "≤ 120 mg/dL"],
        ["Resting ECG", ecg_labels[ecg_idx]],
        ["Max Heart Rate", str(int(input_data[7]))],
        ["Exercise Angina", "Yes" if int(input_data[8]) == 1 else "No"],
        ["ST Depression", f"{input_data[9]:.1f}"],
        ["ST Slope", slope_labels[slope_idx]]
    ]

    # Create table
    table = Table(data, colWidths=[2.5*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    story.append(Spacer(1, 30))

    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'DisclaimerStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        italic=True
    )
    story.append(Paragraph("Disclaimer: This report is generated for informational purposes only. It does not replace medical consultation. Always seek advice from a licensed doctor for proper diagnosis and treatment.", disclaimer_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def home():
    index_path = os.path.join(REACT_BUILD_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return jsonify({
        'status': 'online',
        'service': 'CardioPredict Heart Disease Diagnostic System',
        'message': 'React frontend build available at /index.html'
    })

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    stats = db.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'CardioPredict Heart Disease Diagnostic System',
        'port': 5015,
        'model': {
            'classifier': 'RandomForestClassifier (100 Trees)',
            'features_count': 11,
            'feature_names': [
                'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol',
                'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'
            ]
        },
        'database': {
            'status': stats['status'],
            'total_assessments': stats['total_assessments']
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json or {}
    try:
        age = int(data.get('Age', 50))
        sex = int(data.get('Sex', 1))
        cpt = int(data.get('ChestPainType', 0))
        rbp = int(data.get('RestingBP', 120))
        chol = int(data.get('Cholesterol', 200))
        fbs = int(data.get('FastingBS', 0))
        ecg = int(data.get('RestingECG', 0))
        maxhr = int(data.get('MaxHR', 150))
        exang = int(data.get('ExerciseAngina', 0))
        oldpeak = float(data.get('Oldpeak', 0.0))
        slope = int(data.get('ST_Slope', 1))
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input parameters: {str(e)}'}), 400

    features = [age, sex, cpt, rbp, chol, fbs, ecg, maxhr, exang, oldpeak, slope]
    input_data = np.array([features])
    
    prediction = int(model.predict(input_data)[0])
    is_risk = (prediction == 1)

    probabilities = model.predict_proba(input_data)[0]
    healthy_prob = round(float(probabilities[0]) * 100, 1)
    disease_prob = round(float(probabilities[1]) * 100, 1)

    if disease_prob >= 75.0:
        risk_tier = "High"
    elif disease_prob >= 50.0:
        risk_tier = "Elevated"
    elif disease_prob >= 25.0:
        risk_tier = "Moderate"
    else:
        risk_tier = "Low"

    if is_risk:
        result = "🚨 Heart Disease Detected!"
    else:
        result = "✅ No Heart Disease Detected!"

    # Persist assessment in SQLite
    rec_id = None
    try:
        rec_id = db.log_assessment(
            age, sex, cpt, rbp, chol, fbs, ecg, maxhr, exang, oldpeak, slope,
            prediction, disease_prob, risk_tier
        )
    except Exception as e:
        print(f"Warning: failed to log assessment to DB: {e}")

    return jsonify({
        "prediction": prediction,
        "result_text": result,
        "probability": disease_prob,
        "healthy_probability": healthy_prob,
        "disease_probability": disease_prob,
        "risk_tier": risk_tier,
        "features": features,
        "assessment_id": rec_id
    })

@app.route('/api/download-report', methods=['POST'])
def download_report():
    data = request.json or {}
    prediction_result = data.get('prediction_result', 'Clinical Assessment')
    input_data = data.get('input_data', [])
    
    pdf_buffer = generate_pdf_report(prediction_result, input_data)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Heart_Disease_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', default=25, type=int)
    records = db.get_recent_assessments(limit=limit)
    return jsonify({'success': True, 'records': records, 'count': len(records)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({'success': True, 'stats': db.get_stats()})

# Catch-all route: lets React Router handle all frontend routes
@app.route('/<path:path>')
def catch_all(path):
    file_path = os.path.join(REACT_BUILD_DIR, path)
    if os.path.exists(file_path):
        return send_file(file_path)
    index_path = os.path.join(REACT_BUILD_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return jsonify({'error': 'React build not found.'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5015))
    print(f"[*] Starting CardioPredict Diagnostic Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
