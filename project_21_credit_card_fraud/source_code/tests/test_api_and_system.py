import os
import sys
import unittest
import json

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app, evaluate_transaction, compute_feature_attributions, FEATURE_NAMES, CRITICAL_FEATURES
import database

class TestCreditCardFraudSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        database.init_db()

    # ─────────────────────────────────────────────────────────────
    # 1. Feature Attribution & Model Evaluation Logic
    # ─────────────────────────────────────────────────────────────
    def test_01_feature_names_integrity(self):
        self.assertEqual(len(FEATURE_NAMES), 30)
        self.assertEqual(FEATURE_NAMES[0], 'Time')
        self.assertEqual(FEATURE_NAMES[1], 'Amount')
        self.assertEqual(FEATURE_NAMES[2], 'V1')
        self.assertEqual(FEATURE_NAMES[29], 'V28')

    def test_02_critical_features_configuration(self):
        self.assertIn('V14', CRITICAL_FEATURES)
        self.assertIn('V4', CRITICAL_FEATURES)
        self.assertIn('V12', CRITICAL_FEATURES)
        self.assertIn('V10', CRITICAL_FEATURES)
        self.assertTrue(CRITICAL_FEATURES['V14']['neg_impact'])
        self.assertFalse(CRITICAL_FEATURES['V4']['neg_impact'])

    def test_03_compute_feature_attributions(self):
        feat = {'Amount': 4500.0, 'V14': -5.8, 'V4': 4.2}
        attribs = compute_feature_attributions(feat, 0.95)
        self.assertIsInstance(attribs, list)
        self.assertEqual(len(attribs), 30)
        top = attribs[0]
        self.assertIn('feature', top)
        self.assertIn('impact', top)
        self.assertIn('direction', top)

    def test_04_evaluate_normal_transaction(self):
        feat = {f"V{i}": 0.05 for i in range(1, 29)}
        feat['Amount'] = 35.50
        feat['Time'] = 45000
        res = evaluate_transaction(feat, threshold=0.5)
        self.assertIn('risk_score', res)
        self.assertIn('decision', res)
        self.assertEqual(res['decision'], 'APPROVED')
        self.assertFalse(res['is_fraud'])

    def test_05_evaluate_fraud_transaction(self):
        feat = {f"V{i}": 0.0 for i in range(1, 29)}
        feat['Amount'] = 5800.0
        feat['Time'] = 1200
        feat['V14'] = -6.2
        feat['V4'] = 5.1
        feat['V12'] = -4.9
        feat['V10'] = -4.2
        res = evaluate_transaction(feat, threshold=0.5)
        self.assertIn('risk_score', res)
        self.assertTrue(res['is_fraud'])
        self.assertEqual(res['decision'], 'DECLINED')
        self.assertEqual(res['risk_level'], 'CRITICAL')

    # ─────────────────────────────────────────────────────────────
    # 2. Database Layer Verification
    # ─────────────────────────────────────────────────────────────
    def test_06_database_connection(self):
        conn = database.get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_07_database_add_and_retrieve_transaction(self):
        test_rec = {
            'timestamp': '2026-10-20T00:00:00Z',
            'card_id': 'CARD-TEST-001',
            'merchant': 'UnitTest Electronics',
            'amount': 250.00,
            'risk_score': 0.12,
            'fraud_probability': 12.0,
            'is_fraud': False,
            'decision': 'APPROVED',
            'risk_level': 'LOW',
            'recommended_action': 'AUTO_APPROVE',
            'features': {'Amount': 250.0, 'V14': 0.1},
            'all_attributions': [{'feature': 'V14', 'impact': 0.01, 'direction': 'NEUTRAL'}]
        }
        txn_id = database.add_transaction(test_rec)
        self.assertIsInstance(txn_id, int)
        all_txns = database.get_all_transactions(limit=10)
        found = any(t['card_id'] == 'CARD-TEST-001' for t in all_txns)
        self.assertTrue(found)

    def test_08_database_card_blocking_and_unblocking(self):
        test_card = 'CARD-SANCTION-999'
        database.block_card_db(test_card, reason='Test Fraud Sanction')
        blocked = database.get_blocked_cards_db()
        ids = [b['card_id'] for b in blocked]
        self.assertIn(test_card, ids)

        database.unblock_card_db(test_card)
        blocked_after = database.get_blocked_cards_db()
        ids_after = [b['card_id'] for b in blocked_after]
        self.assertNotIn(test_card, ids_after)

    def test_09_database_audit_logging(self):
        database.log_audit('TEST_AUDIT_ACTION', 'Unit test audit event')
        logs = database.get_audit_logs(limit=10)
        self.assertGreaterEqual(len(logs), 1)
        actions = [l['action'] for l in logs]
        self.assertIn('TEST_AUDIT_ACTION', actions)

    def test_10_database_model_benchmarks(self):
        benchmarks = database.get_model_benchmarks()
        self.assertGreaterEqual(len(benchmarks), 3)
        names = [b['model_name'] for b in benchmarks]
        self.assertTrue(any('Random Forest' in n for n in names))

    # ─────────────────────────────────────────────────────────────
    # 3. REST API Endpoint Tests
    # ─────────────────────────────────────────────────────────────
    def test_11_api_health(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['port'], 5021)
        self.assertIn('models_loaded', data)
        self.assertTrue(data['models_loaded']['random_forest'])

    def test_12_api_predict_valid_payload(self):
        payload = {
            'merchant': 'Apple Store Flagship',
            'amount': 1999.00,
            'time': 43200,
            'features': {'V14': 0.1, 'V4': -0.2, 'V12': 0.05}
        }
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('decision', data)
        self.assertIn('risk_score', data)
        self.assertIn('fraud_probability', data)
        self.assertIn('top_drivers', data)

    def test_13_api_predict_critical_fraud_payload(self):
        payload = {
            'merchant': 'Shady Crypto Escrow',
            'amount': 4500.00,
            'time': 3600,
            'features': {'V14': -6.5, 'V4': 4.8, 'V12': -4.5, 'V10': -4.1}
        }
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['decision'], 'DECLINED')
        self.assertTrue(data['is_fraud'])
        self.assertEqual(data['risk_level'], 'CRITICAL')

    def test_14_api_stream_next(self):
        res = self.client.get('/api/stream/next')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertIn('card_id', data)
        self.assertIn('risk_score', data)
        self.assertIn('merchant', data)

    def test_15_api_batch_evaluate(self):
        batch = {
            'threshold': 0.5,
            'transactions': [
                {'id': 'TX-B1', 'merchant': 'Starbucks', 'features': {'Amount': 5.50, 'V14': 0.0}},
                {'id': 'TX-B2', 'merchant': 'Luxury Boutique', 'features': {'Amount': 6200.00, 'V14': -6.0, 'V4': 4.5}}
            ]
        }
        res = self.client.post('/api/batch/evaluate', json=batch)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['total_evaluated'], 2)
        self.assertIn('fraud_flagged', data)
        self.assertIn('records', data)

    def test_16_api_get_transactions(self):
        res = self.client.get('/api/transactions?limit=15')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 15)

    def test_17_api_card_block_and_unblock(self):
        card = 'CARD-TEST-BLOCKED-123'
        res_block = self.client.post('/api/card/block', json={'card_id': card, 'reason': 'Compromised CVC'})
        self.assertEqual(res_block.status_code, 200)
        self.assertEqual(res_block.get_json()['status'], 'BLOCKED')

        # Try predicting with blocked card
        res_pred = self.client.post('/api/predict', json={'card_id': card, 'amount': 10.0, 'features': {}})
        self.assertEqual(res_pred.status_code, 200)
        self.assertEqual(res_pred.get_json()['decision'], 'DECLINED')

        # Unblock
        res_unblock = self.client.post('/api/card/unblock', json={'card_id': card})
        self.assertEqual(res_unblock.status_code, 200)
        self.assertEqual(res_unblock.get_json()['status'], 'UNBLOCKED')

    def test_18_api_card_block_missing_id(self):
        res = self.client.post('/api/card/block', json={})
        self.assertEqual(res.status_code, 400)

    def test_19_api_card_unblock_missing_id(self):
        res = self.client.post('/api/card/unblock', json={})
        self.assertEqual(res.status_code, 400)

    def test_20_api_blocked_cards_list(self):
        res = self.client.get('/api/blocked-cards')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)

    def test_21_api_audit_endpoint(self):
        res = self.client.get('/api/audit?limit=25')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_22_api_models_endpoint(self):
        res = self.client.get('/api/models')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 3)

    def test_23_api_benchmarks_endpoint(self):
        res = self.client.get('/api/benchmarks')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)

    def test_24_api_dataset_sample(self):
        res = self.client.get('/api/dataset/sample')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('sample_rows', data)
        self.assertGreater(len(data['sample_rows']), 0)

    def test_25_api_metrics_endpoint(self):
        res = self.client.get('/api/metrics?threshold=0.5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('confusion_matrix', data)
        self.assertIn('accuracy', data)
        self.assertIn('precision', data)
        self.assertIn('recall', data)
        self.assertIn('f1_score', data)
        self.assertIn('roc_curve', data)

    def test_26_api_stats_endpoint(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_transactions', data)
        self.assertIn('fraud_detected', data)
        self.assertIn('total_volume_usd', data)
        self.assertIn('fraud_rate', data)

    def test_27_api_export_report_endpoint(self):
        res = self.client.get('/api/export/report')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('report_title', data)
        self.assertIn('summary', data)
        self.assertIn('transaction_ledger', data)

    def test_28_frontend_index_serving(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Credit Card Fraud Detection', res.data)

if __name__ == '__main__':
    unittest.main()
