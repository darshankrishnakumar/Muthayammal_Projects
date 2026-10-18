import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'predictions.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            prediction_date TEXT NOT NULL,
            gender TEXT NOT NULL,
            senior_citizen INTEGER NOT NULL,
            partner INTEGER NOT NULL,
            dependents INTEGER NOT NULL,
            tenure INTEGER NOT NULL,
            phone_service INTEGER NOT NULL,
            multiple_lines INTEGER NOT NULL,
            internet_service TEXT NOT NULL,
            online_security INTEGER NOT NULL,
            online_backup INTEGER NOT NULL,
            device_protection INTEGER NOT NULL,
            tech_support INTEGER NOT NULL,
            streaming_tv INTEGER NOT NULL,
            streaming_movies INTEGER NOT NULL,
            contract TEXT NOT NULL,
            paperless_billing INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            monthly_charges REAL NOT NULL,
            total_charges REAL NOT NULL,
            prediction_status TEXT NOT NULL,
            churn_probability REAL NOT NULL,
            risk_level TEXT NOT NULL,
            cltv REAL NOT NULL,
            action_suggested TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(record):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (
            customer_id, prediction_date, gender, senior_citizen, partner, dependents,
            tenure, phone_service, multiple_lines, internet_service, online_security,
            online_backup, device_protection, tech_support, streaming_tv, streaming_movies,
            contract, paperless_billing, payment_method, monthly_charges, total_charges,
            prediction_status, churn_probability, risk_level, cltv, action_suggested
        ) VALUES (
            :customer_id, :prediction_date, :gender, :senior_citizen, :partner, :dependents,
            :tenure, :phone_service, :multiple_lines, :internet_service, :online_security,
            :online_backup, :device_protection, :tech_support, :streaming_tv, :streaming_movies,
            :contract, :paperless_billing, :payment_method, :monthly_charges, :total_charges,
            :prediction_status, :churn_probability, :risk_level, :cltv, :action_suggested
        )
    ''', record)
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_recent_predictions(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_predictions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_prediction_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM predictions')
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as churn FROM predictions WHERE prediction_status = 'Churn'")
    churn = cursor.fetchone()['churn']
    
    conn.close()
    stay = total - churn
    rate = round((churn / total * 100), 2) if total > 0 else 0.0
    return {
        'total': total,
        'churn': churn,
        'stay': stay,
        'rate': rate
    }

if __name__ == '__main__':
    init_db()
    print("Database initialized at", DB_PATH)
