import os
import sys
import unittest
import sqlite3
import json
import torch

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, SOURCE_DIR)

from phishing_engine import (
    PhishingEngine,
    RCNNAttentionModel,
    AttentionLayer,
    BiLSTMModel,
    LSTMModel,
    GRUModel,
    extract_header_features,
)
from app import app, init_db, DB_PATH


class TestPhishingSystemAndML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = PhishingEngine()
        cls.client = app.test_client()
        init_db()

    def test_rcnn_model_initialization(self):
        """Verify RCNN model architecture parameters and layers."""
        model = self.engine.rcnn_model
        self.assertIsInstance(model, RCNNAttentionModel)
        self.assertTrue(hasattr(model, 'word_embed'))
        self.assertTrue(hasattr(model, 'char_conv'))
        self.assertTrue(hasattr(model, 'bilstm'))
        self.assertTrue(hasattr(model, 'attention'))
        self.assertTrue(hasattr(model, 'classifier'))

    def test_attention_layer_softmax_sum(self):
        """Verify that attention weights sum to 1.0 across the sequence dimension."""
        attn = AttentionLayer(hidden_dim=32)
        dummy_seq = torch.randn(2, 10, 32)
        context, weights = attn(dummy_seq)
        self.assertEqual(context.shape, (2, 32))
        self.assertEqual(weights.shape, (2, 10))
        # Sum of attention weights across tokens must equal 1.0
        sums = torch.sum(weights, dim=1).detach().numpy()
        for s in sums:
            self.assertAlmostEqual(s, 1.0, places=4)

    def test_multilevel_tensor_shapes(self):
        """Verify character and word tensor generation shapes."""
        cleaned_text = "urgent verify your account password immediately"
        word_t = self.engine._texts_to_padded_tensor([cleaned_text])
        char_t = self.engine._texts_to_char_tensor([cleaned_text])
        self.assertEqual(word_t.shape, (1, 100))
        self.assertEqual(char_t.shape, (1, 100))

    def test_rcnn_forward_pass_execution(self):
        """Verify full forward pass output probability is bounded in [0, 1]."""
        model = self.engine.rcnn_model
        model.eval()
        word_t = self.engine._texts_to_padded_tensor(["hello security check world"])
        char_t = self.engine._texts_to_char_tensor(["hello security check world"])
        hdr_t = torch.zeros((1, 8), dtype=torch.float32)

        with torch.no_grad():
            prob, attn = model(word_t, char_t, hdr_t)
        self.assertEqual(prob.shape, (1, 1))
        self.assertEqual(attn.shape, (1, 100))
        val = prob.item()
        self.assertGreaterEqual(val, 0.0)
        self.assertLessEqual(val, 1.0)

    def test_header_feature_extraction(self):
        """Verify extraction of 8-dimensional header feature vectors."""
        feats = extract_header_features(
            from_hdr="security@paypal-security.com",
            subject_hdr="URGENT: Suspended Account Notice",
            reply_to_hdr="fraud@hacker-server.xyz",
            spf_dkim_hdr="fail"
        )
        self.assertEqual(len(feats), 8)
        self.assertEqual(feats[0], 1.0) # Domain mismatch
        self.assertEqual(feats[1], 1.0) # SPF fail
        self.assertEqual(feats[2], 1.0) # Urgent subject

    def test_baseline_models_availability(self):
        """Verify all 8 baseline models (DL + ML) are instantiated."""
        self.assertIn('bilstm', self.engine.dl_models)
        self.assertIn('lstm', self.engine.dl_models)
        self.assertIn('gru', self.engine.dl_models)
        self.assertIn('sgd', self.engine.ml_models)
        self.assertIn('mlp', self.engine.ml_models)
        self.assertIn('logistic_regression', self.engine.ml_models)
        self.assertIn('random_forest', self.engine.ml_models)
        self.assertIn('naive_bayes', self.engine.ml_models)

    def test_phishing_detection_bank_sample(self):
        """Test phishing detection on bank spoofing attack."""
        res = self.engine.analyze_email_multilevel(
            from_hdr="security-alert@chase-secure-verify.com",
            reply_to_hdr="fraud-harvest@server-host.xyz",
            subject_hdr="URGENT: Immediate Account Suspension - Verification Required",
            spf_dkim_hdr="fail",
            email_body="Dear Customer, unauthorized login attempt detected. Verify your credentials: http://chase-secure-verify.com/login",
            selected_model="rcnn_attn"
        )
        self.assertTrue(res['is_phishing'])
        self.assertGreaterEqual(res['phishing_probability'], 80.0)
        self.assertIn("CRITICAL", res['threat_level'])

    def test_legitimate_detection_corporate_sync(self):
        """Test that legitimate corporate email is classified as safe."""
        res = self.engine.analyze_email_multilevel(
            from_hdr="alex.chen@techcorp.internal",
            reply_to_hdr="alex.chen@techcorp.internal",
            subject_hdr="Engineering Team: Daily Sync & Sprint Review at 2:00 PM",
            spf_dkim_hdr="pass",
            email_body="Hi team, quick reminder about our daily standup meeting in Conference Room B. Agenda is sprint 42 status.",
            selected_model="rcnn_attn"
        )
        self.assertFalse(res['is_phishing'])
        self.assertLessEqual(res['phishing_probability'], 25.0)
        self.assertEqual(res['threat_level'], "LEGITIMATE / AUTHENTICATED")

    def test_attention_heatmap_generation(self):
        """Verify attention heatmap generates token weights and identifies threat tokens."""
        res = self.engine.analyze_email_multilevel(
            from_hdr="alerts@bank.com",
            reply_to_hdr="alerts@bank.com",
            subject_hdr="Important notice",
            spf_dkim_hdr="pass",
            email_body="Please verify your secret password immediately.",
            selected_model="rcnn_attn"
        )
        tokens = res['token_attention_heatmap']
        self.assertGreater(len(tokens), 0)
        words = [t['word'] for t in tokens]
        self.assertIn("password", words)
        pwd_token = next(t for t in tokens if t['word'] == 'password')
        self.assertTrue(pwd_token['is_threat_token'])

    def test_unbalanced_dataset_guarantee_metrics(self):
        """Verify benchmark specifications meet academic requirements."""
        benchmarks = self.engine.benchmark_data
        self.assertIn("RCNN + Multilevel Attention (Proposed)", benchmarks)
        rcnn_bench = benchmarks["RCNN + Multilevel Attention (Proposed)"]
        self.assertGreaterEqual(rcnn_bench['recall'], 99.0)
        self.assertGreaterEqual(rcnn_bench['specificity'], 99.0)
        self.assertLess(float(rcnn_bench['unbalanced_eval']['false_positives'].replace('%', '')), 0.5)

    def test_sqlite_database_tables_and_columns(self):
        """Verify SQLite database table existence and schema."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(email_scans)")
        cols = {row[1]: row[2] for row in cur.fetchall()}
        conn.close()
        self.assertIn('id', cols)
        self.assertIn('timestamp', cols)
        self.assertIn('from_hdr', cols)
        self.assertIn('subject_hdr', cols)
        self.assertIn('is_phishing', cols)
        self.assertIn('phishing_probability', cols)
        self.assertIn('threat_level', cols)
        self.assertIn('latency_ms', cols)

    def test_sqlite_historical_seeding(self):
        """Verify historical scans exist in SQLite database."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM email_scans")
        count = cur.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(count, 6)

    def test_api_health_endpoint(self):
        """Test /health endpoint schema and status."""
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['port'], 5017)
        self.assertIn('SQLite Connected', data['database'])

    def test_api_samples_endpoint(self):
        """Test /api/samples returns all 6 benchmark presets."""
        resp = self.client.get('/api/samples')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['samples']), 6)

    def test_api_benchmark_endpoint(self):
        """Test /api/benchmark returns multi-model benchmark metrics."""
        resp = self.client.get('/api/benchmark')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('benchmarks', data)
        self.assertIn('RCNN + Multilevel Attention (Proposed)', data['benchmarks'])

    def test_api_history_endpoint(self):
        """Test /api/history returns recorded scan history."""
        resp = self.client.get('/api/history')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['count'], 6)
        self.assertIsInstance(data['history'], list)

    def test_api_stats_endpoint(self):
        """Test /api/stats returns aggregate metrics."""
        resp = self.client.get('/api/stats')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        stats = data['stats']
        self.assertGreaterEqual(stats['total_scans'], 6)
        self.assertIn('phishing_detected', stats)
        self.assertIn('legitimate_verified', stats)
        self.assertIn('avg_latency_ms', stats)

    def test_api_predict_empty_content_validation(self):
        """Test /api/predict rejects empty input with 400 error."""
        resp = self.client.post('/api/predict', json={'email_text': '', 'subject': ''})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn('error', data)

    def test_api_predict_live_inference_and_db_logging(self):
        """Test live inference writes record to SQLite and returns scan_id."""
        payload = {
            "from": "security-alert@chase-secure-verify.com",
            "reply_to": "fraud-harvest@server-host.xyz",
            "spf_dkim": "fail",
            "subject": "URGENT: Immediate Account Suspension - Verification Required",
            "email_text": "Dear Valued Customer, verify your credentials at http://chase-secure-verify.com/login",
            "model": "rcnn_attn"
        }
        resp = self.client.post('/api/predict', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        scan_data = data['data']
        self.assertIn('scan_id', scan_data)
        self.assertTrue(scan_data['is_phishing'])
        self.assertGreater(scan_data['latency_ms'], 0.0)

        # Verify record exists in SQLite
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT from_hdr, is_phishing, threat_level FROM email_scans WHERE id = ?", (scan_data['scan_id'],))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "security-alert@chase-secure-verify.com")
        self.assertEqual(row[1], 1)

    def test_ensemble_model_selection(self):
        """Test running multi-model consensus ensemble."""
        payload = {
            "from": "alex.chen@techcorp.internal",
            "reply_to": "alex.chen@techcorp.internal",
            "spf_dkim": "pass",
            "subject": "Engineering Team: Daily Sync & Sprint Review at 2:00 PM",
            "email_text": "Hi everyone, quick reminder about our daily sprint sync scheduled for today at 2:00 PM in Conference Room B. Please make sure your backlog is updated.",
            "model": "ensemble"
        }
        resp = self.client.post('/api/predict', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()['data']
        self.assertFalse(data['is_phishing'])
        self.assertEqual(data['selected_model'], 'ensemble')


if __name__ == '__main__':
    unittest.main()
