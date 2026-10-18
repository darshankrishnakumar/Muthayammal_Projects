import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from database import init_db, get_db, save_prediction, get_prediction_stats

def seed_database_if_empty(model, survmodel, sample_size=15):
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM predictions')
    count = cursor.fetchone()['cnt']
    conn.close()

    if count >= sample_size:
        return

    csv_path = os.path.join(os.path.dirname(__file__), 'Telco-Customer-Churn.csv')
    if not os.path.exists(csv_path):
        return

    raw_df = pd.read_csv(csv_path)
    sample_df = raw_df.head(sample_size)

    now = datetime.now()

    for idx, row in sample_df.iterrows():
        # Preprocessing row for model
        gender = 1 if row['gender'] == 'Female' else 0
        senior = int(row['SeniorCitizen'])
        partner = 1 if row['Partner'] == 'Yes' else 0
        dependents = 1 if row['Dependents'] == 'Yes' else 0
        tenure = int(row['tenure'])
        phone = 1 if row['PhoneService'] == 'Yes' else 0
        multlines = 1 if row['MultipleLines'] == 'Yes' else 0
        
        no_internet = 1 if row['InternetService'] == 'No' else 0
        fiber = 1 if row['InternetService'] == 'Fiber optic' else 0
        
        onlinesec = 1 if row['OnlineSecurity'] == 'Yes' else 0
        onlinebackup = 1 if row['OnlineBackup'] == 'Yes' else 0
        deviceprot = 1 if row['DeviceProtection'] == 'Yes' else 0
        techsupp = 1 if row['TechSupport'] == 'Yes' else 0
        streamtv = 1 if row['StreamingTV'] == 'Yes' else 0
        streammov = 1 if row['StreamingMovies'] == 'Yes' else 0
        
        contract_1yr = 1 if row['Contract'] == 'One year' else 0
        contract_2yr = 1 if row['Contract'] == 'Two year' else 0
        
        pay_cc = 1 if 'Credit card' in str(row['PaymentMethod']) else 0
        pay_elec = 1 if 'Electronic check' in str(row['PaymentMethod']) else 0
        pay_mail = 1 if 'Mailed check' in str(row['PaymentMethod']) else 0
        paperless = 1 if row['PaperlessBilling'] == 'Yes' else 0
        
        monthly = float(row['MonthlyCharges'])
        try:
            total_charges = float(row['TotalCharges'])
        except (ValueError, TypeError):
            total_charges = monthly * tenure

        features = [
            gender, senior, partner, dependents, tenure, phone, multlines,
            onlinesec, onlinebackup, deviceprot, techsupp, streamtv, streammov,
            paperless, monthly, total_charges, fiber, no_internet,
            contract_1yr, contract_2yr, pay_cc, pay_elec, pay_mail
        ]

        prob = float(model.predict_proba([np.array(features)])[0, 1])
        status = 'Churn' if prob >= 0.50 else 'No Churn'

        if prob >= 0.60:
            risk = 'High'
            action = 'High risk: Immediate outreach recommended. Evaluate promotional discounts or annual contract conversion.'
        elif prob >= 0.35:
            risk = 'Medium'
            action = 'Moderate risk: Monitor usage trends, offer personalized service bundles, and schedule check-in call.'
        else:
            risk = 'Low'
            action = 'Low risk: Customer shows healthy engagement. Maintain standard communication and loyalty rewards.'

        # Compute CLTV from survmodel
        surv_feats = np.array([
            gender, senior, partner, dependents, phone, multlines,
            onlinesec, onlinebackup, deviceprot, techsupp, streamtv, streammov,
            paperless, monthly, total_charges, fiber, no_internet,
            contract_1yr, contract_2yr, pay_cc, pay_elec, pay_mail
        ]).reshape(1, -1)

        try:
            life = survmodel.predict_survival_function(surv_feats).reset_index()
            life.columns = ['Tenure', 'Probability']
            max_life = life.Tenure[life.Probability > 0.1].max()
            cltv = round(float(max_life * monthly), 2)
        except Exception:
            cltv = round(float(24 * monthly), 2)

        # Distribute seed dates over the past 14 days
        pred_date = (now - timedelta(days=random.randint(0, 14), hours=random.randint(1, 23))).strftime('%Y-%m-%d %H:%M:%S')

        record = {
            'customer_id': str(row['customerID']),
            'prediction_date': pred_date,
            'gender': row['gender'],
            'senior_citizen': senior,
            'partner': partner,
            'dependents': dependents,
            'tenure': tenure,
            'phone_service': phone,
            'multiple_lines': multlines,
            'internet_service': row['InternetService'],
            'online_security': onlinesec,
            'online_backup': onlinebackup,
            'device_protection': deviceprot,
            'tech_support': techsupp,
            'streaming_tv': streamtv,
            'streaming_movies': streammov,
            'contract': row['Contract'],
            'paperless_billing': paperless,
            'payment_method': row['PaymentMethod'],
            'monthly_charges': monthly,
            'total_charges': total_charges,
            'prediction_status': status,
            'churn_probability': round(prob, 4),
            'risk_level': risk,
            'cltv': cltv,
            'action_suggested': action
        }
        save_prediction(record)

    print("Seeded database with initial genuine Telco records.")
