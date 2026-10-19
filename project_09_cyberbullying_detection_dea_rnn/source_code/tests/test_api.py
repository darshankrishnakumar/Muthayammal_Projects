import os
import sys
import unittest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app, get_db

class TestCyberbullyingAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_serves_frontend(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("DEA-RNN", response.text)

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['models_loaded'])

    def test_api_stats(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_scanned', data)
        self.assertIn('cyberbullying_detected', data)
        self.assertIn('clean_tweets', data)
        self.assertIn('toxicity_rate', data)
        self.assertGreaterEqual(data['total_scanned'], 1)

    def test_api_metrics(self):
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('accuracy', data)
        self.assertGreaterEqual(data['accuracy'], 0.90)
        self.assertIn('f1_score', data)
        self.assertIn('confusion_matrix', data)

    def test_api_history(self):
        response = self.client.get('/api/history?limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_predict_clean_tweet(self):
        payload = {"text": "Hope everyone has a wonderful and productive Monday! Let's get to work #positive"}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'not_cyberbullying')
        self.assertFalse(data['is_cyberbullying'])
        self.assertEqual(data['moderation_action'], 'APPROVED FOR BROADCAST')

    def test_predict_gender_cyberbullying(self):
        payload = {"text": "Women should stay in the kitchen and stop pretending they understand engineering or logic."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'gender')
        self.assertTrue(data['is_cyberbullying'])

    def test_predict_religion_cyberbullying(self):
        payload = {"text": "Your religion is a violent cult of brainwashed extremists who want to destroy modern civilization."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'religion')
        self.assertTrue(data['is_cyberbullying'])

    def test_predict_age_cyberbullying(self):
        payload = {"text": "Ok boomer, hurry up and retire so competent younger people can actually fix your mess."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'age')
        self.assertTrue(data['is_cyberbullying'])

    def test_predict_ethnicity_cyberbullying(self):
        payload = {"text": "Go back to your third world country where you belong, nobody invited you immigrants here."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'ethnicity')
        self.assertTrue(data['is_cyberbullying'])

    def test_predict_other_cyberbullying(self):
        payload = {"text": "You are the most pathetic waste of oxygen on this platform, literally nobody would care if you vanished."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['predicted_category'], 'other_cyberbullying')
        self.assertTrue(data['is_cyberbullying'])

    def test_predict_probability_distribution(self):
        payload = {"text": "Just finished reading an incredible book on artificial intelligence."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        probs = data['probabilities']
        self.assertEqual(len(probs), 6)
        prob_sum = sum(probs.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=2)

    def test_predict_token_attentions(self):
        payload = {"text": "Cooking some homemade pasta tonight with fresh basil and garlic from the garden."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        tokens = data['token_attentions']
        self.assertGreater(len(tokens), 0)
        weight_sum = sum(t['weight'] for t in tokens)
        self.assertAlmostEqual(weight_sum, 1.0, places=2)

    def test_predict_database_persistence(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM scans")
        cnt_before = cur.fetchone()['cnt']
        conn.close()

        payload = {"text": "Testing database transaction logging for DEA-RNN inference audit trail."}
        response = self.client.post('/api/predict', json=payload)
        self.assertEqual(response.status_code, 200)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM scans")
        cnt_after = cur.fetchone()['cnt']
        conn.close()
        self.assertEqual(cnt_after, cnt_before + 1)

    def test_predict_empty_text_error(self):
        response = self.client.post('/api/predict', json={"text": "   "})
        self.assertEqual(response.status_code, 400)

    def test_batch_prediction(self):
        payload = {
            "texts": [
                "Good morning and have a blessed day!",
                "Typical dumb blonde, go back to doing your makeup.",
                "Happy birthday to my best friend!"
            ]
        }
        response = self.client.post('/api/batch', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_processed'], 3)
        self.assertEqual(len(data['results']), 3)

if __name__ == '__main__':
    unittest.main()
