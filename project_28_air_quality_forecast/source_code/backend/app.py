import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import database
from forecast_engine import get_forecast_engine, AQI_CLASSES

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Initialize and seed database
database.init_db()
database.seed_database()

# Load Deep Neural Engine
engine = get_forecast_engine()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    stats = database.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'Urban Air Quality (AQI) Deep Learning Forecasting API',
        'port': 5028,
        'model_architecture': 'PyTorch 2-Layer BiLSTM + 4-Layer Hazard MLP Classifier',
        'database_backend': 'SQLite ACID Relational DB (air_quality.db)',
        'total_historical_records': stats['total_historical_records'],
        'monitoring_stations': stats['total_monitoring_stations'],
        'average_latency_ms': stats['average_inference_latency_ms']
    })

@app.route('/api/model/metadata', methods=['GET'])
def model_metadata():
    return jsonify(engine.metadata)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = database.get_stats()
    return jsonify(stats)

@app.route('/api/cities', methods=['GET'])
def get_cities():
    stations = database.get_stations()
    return jsonify([
        {
            'name': s['city'],
            'station_id': s['station_id'],
            'country': s['country'],
            'base': s['base_aqi'],
            'temp': s['temp'],
            'humidity': s['humidity'],
            'wind': s['wind'],
            'blh': s['blh']
        } for s in stations
    ])

@app.route('/api/forecast', methods=['POST'])
def forecast():
    data = request.json or {}
    city = data.get('city', 'Delhi')
    days = min(int(data.get('days', 7)), 14)

    station_meta = database.get_station_by_city(city)
    recent = database.get_recent_readings(city, limit=24)

    result = engine.predict_forecast(city, days=days, recent_readings=recent, station_meta=station_meta)
    fid = database.log_forecast_result(result)
    result['forecast_id'] = fid

    return jsonify(result)

@app.route('/api/predict/custom', methods=['POST'])
def predict_custom():
    data = request.json or {}
    try:
        pm25 = float(data.get('pm25', 45.0))
        pm10 = float(data.get('pm10', 80.0))
        no2 = float(data.get('no2', 30.0))
        so2 = float(data.get('so2', 12.0))
        co = float(data.get('co', 1.0))
        o3 = float(data.get('o3', 40.0))
        temp = float(data.get('temp', 25.0))
        humidity = float(data.get('humidity', 60.0))
        wind = float(data.get('wind', 10.0))
        blh = float(data.get('blh', 800.0))

        feat = [pm25, pm10, no2, so2, co, o3, temp, humidity, wind, blh]
        cls_res = engine.classify_instant(feat)
        return jsonify({
            'status': 'success',
            'input_pollutants': {'pm25': pm25, 'pm10': pm10, 'no2': no2, 'so2': so2, 'co': co, 'o3': o3},
            'meteorology': {'temp': temp, 'humidity': humidity, 'wind': wind, 'blh': blh},
            **cls_res
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = int(request.args.get('limit', 10))
    history = database.get_history(limit=limit)
    return jsonify(history)

@app.route('/api/readings/<city>', methods=['GET'])
def get_city_readings(city):
    limit = int(request.args.get('limit', 24))
    readings = database.get_recent_readings(city, limit=limit)
    return jsonify(readings)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5028))
    print(f"=================================================================")
    print(f"🚀 Urban Air Quality Deep Learning Forecasting API (PROJECT-028)")
    print(f"🔒 Dedicated Port: Port {port} (http://127.0.0.1:{port}/)")
    print(f"🧠 Engine: PyTorch BiLSTM (Sequence) + 4-Layer Hazard MLP")
    print(f"💾 Database: SQLite ACID Ledger (air_quality.db)")
    print(f"=================================================================")
    app.run(debug=False, host='0.0.0.0', port=port)
