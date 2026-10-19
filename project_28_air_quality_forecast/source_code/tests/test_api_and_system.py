import os
import sys
import unittest
import json
import torch
import numpy as np

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
from forecast_engine import get_forecast_engine, get_aqi_meta, AQI_CLASSES
from app import app

class TestAirQualityForecastSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.seed_database(force=True)
        cls.engine = get_forecast_engine()
        cls.client = app.test_client()

    # 1. Health Endpoint
    def test_01_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['port'], 5028)
        self.assertIn('BiLSTM', data['model_architecture'])
        self.assertEqual(data['total_historical_records'], 5500)
        self.assertEqual(data['monitoring_stations'], 10)

    # 2. Model Metadata Endpoint
    def test_02_model_metadata(self):
        res = self.client.get('/api/model/metadata')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['project_id'], 'PROJECT-028')
        self.assertEqual(data['bilstm_architecture']['output_horizon_hours'], 24)
        self.assertEqual(len(data['classifier_architecture']['output_classes']), 6)
        self.assertGreater(data['classifier_architecture']['test_accuracy'], 0.90)

    # 3. Stats Endpoint
    def test_03_stats_endpoint(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['total_historical_records'], 5500)
        self.assertEqual(data['total_monitoring_stations'], 10)
        self.assertEqual(data['database_mode'], 'SQLite ACID (WAL Enabled)')

    # 4. Cities Endpoint
    def test_04_cities_endpoint(self):
        res = self.client.get('/api/cities')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 10)
        names = [c['name'] for c in data]
        self.assertIn('Delhi', names)
        self.assertIn('London', names)
        self.assertIn('Tokyo', names)
        self.assertIn('Paris', names)

    # 5. Delhi Forecast (High AQI Metro)
    def test_05_delhi_forecast_bilstm(self):
        res = self.client.post('/api/forecast', json={'city': 'Delhi', 'days': 7})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['city'], 'Delhi')
        self.assertEqual(len(data['hourly_trend']), 24)
        self.assertEqual(len(data['daily_forecast']), 7)
        self.assertGreater(data['current']['aqi'], 120)
        self.assertIn('forecast_id', data)

    # 6. London Forecast (Clean Air Baseline)
    def test_06_london_forecast_bilstm(self):
        res = self.client.post('/api/forecast', json={'city': 'London', 'days': 7})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['city'], 'London')
        self.assertLess(data['current']['aqi'], 100)
        self.assertIn(data['current']['hazard_class'], ['Good', 'Moderate'])

    # 7. Tokyo Forecast
    def test_07_tokyo_forecast_bilstm(self):
        res = self.client.post('/api/forecast', json={'city': 'Tokyo', 'days': 5})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data['daily_forecast']), 5)
        self.assertLess(data['current']['aqi'], 80)

    # 8. Custom Predict: Clean Air (Good)
    def test_08_custom_predict_clean_air(self):
        payload = {
            'pm25': 8.0, 'pm10': 18.0, 'no2': 12.0, 'so2': 4.0, 'co': 0.4,
            'o3': 28.0, 'temp': 20.0, 'humidity': 50.0, 'wind': 15.0, 'blh': 1100.0
        }
        res = self.client.post('/api/predict/custom', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['hazard_class'], 'Good')
        self.assertGreater(data['confidence'], 0.70)

    # 9. Custom Predict: Hazardous Air
    def test_09_custom_predict_hazardous_air(self):
        payload = {
            'pm25': 380.0, 'pm10': 550.0, 'no2': 140.0, 'so2': 65.0, 'co': 4.8,
            'o3': 95.0, 'temp': 34.0, 'humidity': 85.0, 'wind': 2.0, 'blh': 300.0
        }
        res = self.client.post('/api/predict/custom', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['hazard_class'], 'Hazardous')
        self.assertGreater(data['confidence'], 0.75)

    # 10. Custom Predict: Unhealthy Air
    def test_10_custom_predict_unhealthy_air(self):
        payload = {
            'pm25': 120.0, 'pm10': 190.0, 'no2': 55.0, 'so2': 22.0, 'co': 1.8,
            'o3': 50.0, 'temp': 28.0, 'humidity': 70.0, 'wind': 6.0, 'blh': 600.0
        }
        res = self.client.post('/api/predict/custom', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data['hazard_class'], ['Unhealthy for Sensitive', 'Unhealthy', 'Very Unhealthy'])

    # 11. Relational Database Logging
    def test_11_forecast_database_persistence(self):
        res = self.client.post('/api/forecast', json={'city': 'Mumbai', 'days': 7})
        fid = res.get_json()['forecast_id']
        conn = database.get_connection()
        row = conn.execute("SELECT * FROM forecast_history WHERE forecast_id = ?", (fid,)).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row['city'], 'Mumbai')

    # 12. Hourly Predictions Foreign Key Integrity
    def test_12_hourly_predictions_fk_integrity(self):
        res = self.client.post('/api/forecast', json={'city': 'Bengaluru', 'days': 7})
        fid = res.get_json()['forecast_id']
        conn = database.get_connection()
        rows = conn.execute("SELECT * FROM hourly_predictions WHERE forecast_id = ?", (fid,)).fetchall()
        conn.close()
        self.assertEqual(len(rows), 24)
        for r in rows:
            self.assertEqual(r['forecast_id'], fid)
            self.assertGreater(r['predicted_aqi'], 0)

    # 13. Audit Log Verification
    def test_13_audit_trail_logging(self):
        conn = database.get_connection()
        rows = conn.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 5").fetchall()
        conn.close()
        self.assertGreater(len(rows), 0)
        event_types = [r['event_type'] for r in rows]
        self.assertTrue(any('FORECAST_EXECUTED' in e or 'DATABASE_SEEDED' in e for e in event_types))

    # 14. City Readings Endpoint
    def test_14_recent_readings_endpoint(self):
        res = self.client.get('/api/readings/Delhi?limit=12')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 12)
        self.assertIn('pm25', data[0])
        self.assertIn('boundary_layer_height_m', data[0])

    # 15. History Endpoint
    def test_15_history_endpoint(self):
        res = self.client.get('/api/history?limit=5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('predicted_peak_aqi', data[0])

    # 16. Neural Inference Latency Profiling
    def test_16_bilstm_inference_latency(self):
        res = self.client.post('/api/forecast', json={'city': 'Paris', 'days': 7})
        latency = res.get_json()['inference_latency_ms']
        self.assertLess(latency, 50.0)

    # 17. BiLSTM Output Shape
    def test_17_bilstm_output_shape(self):
        dummy_seq = torch.randn(1, 24, 10)
        with torch.no_grad():
            out = self.engine.bilstm(dummy_seq)
        self.assertEqual(out.shape, (1, 24, 3))

    # 18. Classifier Softmax Sum
    def test_18_classifier_softmax_probabilities(self):
        feat = [50.0, 90.0, 25.0, 10.0, 1.0, 35.0, 25.0, 60.0, 12.0, 850.0]
        res = self.engine.classify_instant(feat)
        prob_sum = sum(res['probabilities'].values())
        self.assertAlmostEqual(prob_sum, 1.0, places=3)

    # 19. Unindexed City Fallback
    def test_19_invalid_city_fallback(self):
        res = self.client.post('/api/forecast', json={'city': 'Atlantis', 'days': 7})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['city'], 'Atlantis')
        self.assertEqual(len(data['daily_forecast']), 7)

    # 20. Days Clamping
    def test_20_days_parameter_clamping(self):
        res = self.client.post('/api/forecast', json={'city': 'Chennai', 'days': 45})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data['daily_forecast']), 14)

    # 21. Frontend Serving
    def test_21_frontend_index_serving(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Urban Air Quality (AQI) Forecasting', res.data)

    # 22. Health Advisories Generation
    def test_22_health_advisories_generation(self):
        res = self.client.post('/api/forecast', json={'city': 'Delhi', 'days': 7})
        advs = res.get_json()['health_advisories']
        self.assertGreater(len(advs), 0)
        titles = [a['title'] for a in advs]
        self.assertTrue(any('Respirator' in t or 'Purifier' in t or 'Caution' in t or 'Outdoor' in t for t in titles))

    # 23. Meteorology Payload
    def test_23_meteorology_payload(self):
        res = self.client.post('/api/forecast', json={'city': 'Kolkata', 'days': 7})
        met = res.get_json()['meteorology']
        self.assertIn('temperature_c', met)
        self.assertIn('humidity_pct', met)
        self.assertIn('wind_speed_kmh', met)
        self.assertIn('boundary_layer_height_m', met)

    # 24. AQI Metadata Boundaries
    def test_24_aqi_scale_boundaries(self):
        self.assertEqual(get_aqi_meta(25)['label'], 'Good')
        self.assertEqual(get_aqi_meta(75)['label'], 'Moderate')
        self.assertEqual(get_aqi_meta(125)['label'], 'Unhealthy for Sensitive')
        self.assertEqual(get_aqi_meta(175)['label'], 'Unhealthy')
        self.assertEqual(get_aqi_meta(250)['label'], 'Very Unhealthy')
        self.assertEqual(get_aqi_meta(420)['label'], 'Hazardous')

    # 25. SQLite WAL Mode
    def test_25_sqlite_wal_mode_enabled(self):
        conn = database.get_connection()
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), 'wal')

    # 26. Custom Predict Partial Payload
    def test_26_custom_predict_missing_params(self):
        res = self.client.post('/api/predict/custom', json={'pm25': 55.0})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('hazard_class', data)

    # 27. Feature Scaler Dimension
    def test_27_feature_scaler_dimensions(self):
        self.assertEqual(len(self.engine.means), 10)
        self.assertEqual(len(self.engine.stds), 10)

    # 28. Station Geographic Coverage
    def test_28_station_geographic_coverage(self):
        stations = database.get_stations()
        countries = set([s['country'] for s in stations])
        self.assertTrue(len(countries) >= 4)
        self.assertIn('India', countries)
        self.assertIn('UK', countries)
        self.assertIn('USA', countries)
        self.assertIn('Japan', countries)

if __name__ == '__main__':
    unittest.main()
