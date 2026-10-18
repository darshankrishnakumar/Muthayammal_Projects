import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'airfare.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            airline TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            journey_date TEXT NOT NULL,
            dep_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            duration_mins INTEGER NOT NULL,
            total_stops INTEGER NOT NULL,
            predicted_price_lstm REAL NOT NULL,
            predicted_price_rf REAL NOT NULL,
            recommended_fare REAL NOT NULL,
            confidence_score REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_prediction(airline, source, destination, journey_date, dep_time, arrival_time,
                   duration_mins, total_stops, predicted_price_lstm, predicted_price_rf,
                   recommended_fare, confidence_score):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO flight_predictions (
            timestamp, airline, source, destination, journey_date, dep_time, arrival_time,
            duration_mins, total_stops, predicted_price_lstm, predicted_price_rf,
            recommended_fare, confidence_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        now_str, airline, source, destination, journey_date, dep_time, arrival_time,
        duration_mins, total_stops, round(predicted_price_lstm, 2), round(predicted_price_rf, 2),
        round(recommended_fare, 2), round(confidence_score, 4)
    ))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_recent_predictions(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM flight_predictions ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_analytics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total_queries FROM flight_predictions')
    total = cursor.fetchone()['total_queries']
    
    cursor.execute('''
        SELECT airline, AVG(recommended_fare) as avg_fare, COUNT(*) as query_count
        FROM flight_predictions
        GROUP BY airline
        ORDER BY avg_fare DESC
    ''')
    airline_stats = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute('''
        SELECT source || ' → ' || destination as route, COUNT(*) as route_count, AVG(recommended_fare) as avg_fare
        FROM flight_predictions
        GROUP BY route
        ORDER BY route_count DESC LIMIT 5
    ''')
    route_stats = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        'total_predictions': total,
        'airline_statistics': airline_stats,
        'popular_routes': route_stats
    }

if __name__ == '__main__':
    init_db()
    print(f'Database initialized at: {DB_PATH}')
