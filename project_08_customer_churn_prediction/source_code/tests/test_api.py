import os
import sys
import unittest
import json

CHURN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Customer-Survival-Analysis-and-Churn-Prediction-master'))
if CHURN_DIR not in sys.path:
    sys.path.insert(0, CHURN_DIR)

from app import app
from database import get_db, get_prediction_stats

class TestCustomerChurnAPI(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True

    def test_dashboard_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer", response.data)

    def test_predict_page_render(self):
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"form", response.data.lower())

    def test_performance_page_render(self):
        response = self.client.get('/model-performance')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Performance", response.data)

    def test_history_page_render(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"History", response.data)

    def test_api_stats(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('total', data)
        self.assertIn('churn', data)
        self.assertIn('stay', data)
        self.assertIn('rate', data)
        self.assertIsInstance(data['total'], int)

    def test_api_metrics(self):
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('total_dataset_records', data)
        self.assertEqual(data['total_dataset_records'], 7043)
        self.assertIn('test', data)
        self.assertGreaterEqual(data['test']['accuracy'], 0.70)
        self.assertGreaterEqual(data['test']['roc_auc'], 0.80)

    def test_api_history(self):
        response = self.client.get('/api/history')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_predict_submission_high_risk_churn(self):
        # Month-to-month, Fiber Optic, no tech support, tenure 1
        sample_payload = {
            'gender': '0',
            'SeniorCitizen': '1',
            'Tenure': '1',
            'PhoneService': '1',
            'MultipleLines': '1',
            'InternetService': '2',  # Fiber optic
            'PaperlessBilling': '1',
            'Contract': '0',        # Month-to-month
            'PaymentMethod': '2',   # Electronic check
            'MonthlyCharges': '95.50'
        }
        response = self.client.post('/predict', data=sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Estimated Churn Probability", response.data)
        self.assertIn(b"data:image/png;base64", response.data)
        self.assertIn(b"Suggested Retention Strategy", response.data)

    def test_predict_submission_low_risk_retention(self):
        # Two-year term, DSL, all security add-ons, tenure 65
        sample_payload = {
            'gender': '1',
            'Partner': '1',
            'Dependents': '1',
            'Tenure': '65',
            'PhoneService': '1',
            'MultipleLines': '1',
            'InternetService': '1',  # DSL
            'OnlineSecurity': '1',
            'OnlineBackup': '1',
            'DeviceProtection': '1',
            'TechSupport': '1',
            'Contract': '2',        # Two-year
            'PaymentMethod': '1',   # Credit card
            'MonthlyCharges': '55.20'
        }
        response = self.client.post('/predict', data=sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Estimated Churn Probability", response.data)
        self.assertIn(b"data:image/png;base64", response.data)
        self.assertIn(b"LOW RISK", response.data)

    def test_predict_database_persistence(self):
        initial_stats = get_prediction_stats()
        initial_count = initial_stats['total']
        
        sample_payload = {
            'gender': '1',
            'Tenure': '18',
            'InternetService': '1',
            'Contract': '1',
            'PaymentMethod': '0',
            'MonthlyCharges': '50.00'
        }
        response = self.client.post('/predict', data=sample_payload)
        self.assertEqual(response.status_code, 200)
        
        updated_stats = get_prediction_stats()
        self.assertEqual(updated_stats['total'], initial_count + 1)

    def test_invalid_input_error_handling(self):
        sample_payload = {
            'MonthlyCharges': 'INVALID_FLOAT'
        }
        response = self.client.post('/predict', data=sample_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())

if __name__ == '__main__':
    unittest.main()
