"""
Comprehensive Automated QA and System Test Suite for PROJECT-022:
Customer Complaint Classification and Priority Routing Engine.

Covers:
- Model artifact presence and validation
- NLP Vectorization and vocabulary consistency
- Category classification across 6 industrial domains
- Priority classification and uncertainty estimation
- Urgency and sentiment scoring bounds
- Relational SQLite transactional persistence and CRUD operations
- Department and SLA policy enforcement
- Full REST API endpoint testing, error handling, and audit trails
"""

import unittest
import os
import sys
import json
import importlib.util

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "backend"))

sys.path.insert(0, BACKEND_DIR)
import database
from app import app, classify_complaint, CATEGORIES, PRIORITY_RULES

class TestProject022System(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        database.init_db()

    # ─── SECTION 1: MODEL ARTIFACTS & METADATA TESTS ─────────────────────────

    def test_01_model_artifacts_exist(self):
        vec_path = os.path.join(BACKEND_DIR, "tfidf_vectorizer.joblib")
        cat_model_path = os.path.join(BACKEND_DIR, "category_model.joblib")
        prio_model_path = os.path.join(BACKEND_DIR, "priority_model.joblib")
        meta_path = os.path.join(BACKEND_DIR, "model_metadata.json")

        self.assertTrue(os.path.isfile(vec_path), "TF-IDF Vectorizer artifact must exist")
        self.assertTrue(os.path.isfile(cat_model_path), "Category Classifier artifact must exist")
        self.assertTrue(os.path.isfile(prio_model_path), "Priority Classifier artifact must exist")
        self.assertTrue(os.path.isfile(meta_path), "Model metadata JSON must exist")

    def test_02_model_metadata_structure(self):
        meta_path = os.path.join(BACKEND_DIR, "model_metadata.json")
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        self.assertIn("category_model", meta)
        self.assertIn("priority_model", meta)
        self.assertIn("accuracy", meta["category_model"])
        self.assertIn("macro_f1", meta["category_model"])
        self.assertGreaterEqual(meta["category_model"]["accuracy"], 0.85)
        self.assertGreaterEqual(meta["priority_model"]["accuracy"], 0.70)
        self.assertGreater(meta.get("vocab_size", 0), 500)

    def test_03_vectorizer_transformation(self):
        import joblib
        vec = joblib.load(os.path.join(BACKEND_DIR, "tfidf_vectorizer.joblib"))
        X = vec.transform(["Billing dispute regarding unauthorized charge on credit card"])
        self.assertEqual(X.shape[0], 1)
        self.assertGreater(X.nnz, 0, "Sparse matrix should contain non-zero features")

    def test_04_category_classes_coverage(self):
        import joblib
        cat_model = joblib.load(os.path.join(BACKEND_DIR, "category_model.joblib"))
        expected_categories = set(CATEGORIES.keys())
        model_classes = set(cat_model.classes_)
        self.assertTrue(expected_categories.issubset(model_classes) or model_classes.issubset(expected_categories))

    def test_05_priority_classes_coverage(self):
        import joblib
        prio_model = joblib.load(os.path.join(BACKEND_DIR, "priority_model.joblib"))
        expected_priorities = {'critical', 'high', 'medium', 'low'}
        self.assertEqual(set(prio_model.classes_), expected_priorities)

    # ─── SECTION 2: NLP DOMAIN CLASSIFICATION ACCURACY ────────────────────────

    def test_06_classify_payment_issue(self):
        text = "My corporate card was charged $1,490 twice for order #88492. I need an immediate reversal and refund! Unauthorized charge."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'payment_issue')
        self.assertEqual(res['department'], 'FinOps Billing & Fraud Team')
        self.assertGreaterEqual(res['confidence'], 0.80)

    def test_07_classify_product_defect(self):
        text = "The industrial laser printer motor stopped turning after 2 days. The spindle is cracked and burning plastic smell is coming out. RMA needed."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'product_complaint')
        self.assertEqual(res['department'], 'Quality Engineering & RMA Desk')
        self.assertGreaterEqual(res['confidence'], 0.80)

    def test_08_classify_delivery_delay(self):
        text = "Air cargo tracking #ORB-99120 has been stuck in Frankfurt transit for 9 days. Delayed courier package lost in transit."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'delivery_problem')
        self.assertEqual(res['department'], 'Global Supply Chain & Logistics')

    def test_09_classify_technical_outage(self):
        text = "Production API endpoint /v2/telemetry returning HTTP 500 internal server error during high load peaks. App crash and exception."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'technical_issue')
        self.assertEqual(res['department'], 'Tier-3 Engineering & DevOps')

    def test_10_classify_account_lockout(self):
        text = "Our team lead is locked out of the enterprise console after MFA reset. Cannot access password or user administration."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'account_issue')
        self.assertEqual(res['department'], 'Identity & Access Management (IAM)')

    def test_11_classify_service_dissatisfaction(self):
        text = "Your Tier-1 support representative was rude, dismissive, closed my support ticket without resolving the bug. Terrible service."
        res = classify_complaint(text)
        self.assertEqual(res['category'], 'service_dissatisfaction')
        self.assertEqual(res['department'], 'Executive Customer Relations')

    # ─── SECTION 3: PROBABILITY & METRIC INTEGRITY ───────────────────────────

    def test_12_probabilities_sum_to_one(self):
        res = classify_complaint("System outage blocking all user payments.")
        probs = res['probabilities']
        prob_sum = sum(probs.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=2)

    def test_13_urgency_score_range(self):
        res_critical = classify_complaint("Immediate life-safety emergency and data breach!")
        res_low = classify_complaint("Minor question regarding invoice formatting guidelines.")
        self.assertTrue(10 <= res_critical['urgency_score'] <= 100)
        self.assertTrue(10 <= res_low['urgency_score'] <= 100)
        self.assertGreaterEqual(res_critical['urgency_score'], res_low['urgency_score'])

    def test_14_sentiment_score_bounds(self):
        res = classify_complaint("Horrible service and broken equipment.")
        self.assertTrue(-1.0 <= res['sentiment_score'] <= 1.0)

    def test_15_sla_calculation(self):
        res_crit = classify_complaint("Emergency breach requiring immediate fix!")
        self.assertIn("sla_hours", res_crit)
        self.assertIn("sla_deadline", res_crit)
        self.assertLessEqual(res_crit['sla_hours'], 2.0)

    # ─── SECTION 4: RELATIONAL SQLITE DATABASE TESTS ──────────────────────────

    def test_16_database_tables_exist(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for expected in ['complaints', 'departments', 'sla_policies', 'system_audit']:
            self.assertIn(expected, tables)

    def test_17_database_add_and_get_complaint(self):
        sample = {
            'timestamp': '2026-10-20 01:00:00',
            'complaint': 'Test DB persistence complaint text for QA verification.',
            'category': 'technical_issue',
            'category_label': 'Software Bug & Platform Outage',
            'category_icon': '💻',
            'department': 'Tier-3 Engineering & DevOps',
            'priority': 'high',
            'priority_label': 'HIGH',
            'confidence': 0.94,
            'probabilities': {'technical_issue': 0.94, 'account_issue': 0.06},
            'urgency_score': 80,
            'sentiment_score': -0.65,
            'sla_hours': 2.0,
            'sla_deadline': '2026-10-20 03:00 UTC',
            'status': 'PENDING',
            'notes': 'Unit test ticket',
            'matched_keywords': ['test', 'db', 'bug'],
            'summary': 'Unit test ticket summary.'
        }
        t_id = database.add_complaint(sample)
        self.assertIsInstance(t_id, int)
        self.assertGreater(t_id, 0)

        retrieved = database.get_complaint_by_id(t_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['complaint'], sample['complaint'])
        self.assertEqual(retrieved['category'], sample['category'])

    def test_18_database_filter_queries(self):
        all_t = database.get_complaints(limit=10)
        self.assertGreater(len(all_t), 0)

        cat_filtered = database.get_complaints(category='payment_issue', limit=5)
        for t in cat_filtered:
            self.assertEqual(t['category'], 'payment_issue')

    def test_19_database_update_ticket_status(self):
        tickets = database.get_complaints(limit=1)
        self.assertGreater(len(tickets), 0)
        t_id = tickets[0]['id']
        ok = database.update_ticket_status(t_id, 'RESOLVED', notes="Resolved in QA test suite")
        self.assertTrue(ok)
        updated = database.get_complaint_by_id(t_id)
        self.assertEqual(updated['status'], 'RESOLVED')
        self.assertIn("Resolved in QA", updated['notes'])

    def test_20_database_audit_trail_logging(self):
        logs = database.get_audit_logs(limit=10)
        self.assertGreater(len(logs), 0)
        self.assertIn("timestamp", logs[0])
        self.assertIn("event_type", logs[0])
        self.assertIn("outcome", logs[0])

    def test_21_database_stats_aggregation(self):
        stats = database.get_stats()
        self.assertIn("total", stats)
        self.assertIn("by_category", stats)
        self.assertIn("by_priority", stats)
        self.assertIn("avg_urgency", stats)
        self.assertIn("avg_confidence_pct", stats)
        self.assertGreater(stats['total'], 0)

    # ─── SECTION 5: REST API ENDPOINTS TESTS ─────────────────────────────────

    def test_22_api_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("service", data)
        self.assertIn("accuracy_pct", data)

    def test_23_api_classify_endpoint_success(self):
        res = self.client.post("/api/classify", json={
            "complaint": "Unauthorized debit of $350 on my credit card invoice. Please refund immediately!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("id", data)
        self.assertEqual(data["category"], "payment_issue")
        self.assertIn("confidence", data)
        self.assertIn("department", data)
        self.assertIn("urgency_score", data)

    def test_24_api_classify_endpoint_empty_error(self):
        res = self.client.post("/api/classify", json={"complaint": ""})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_25_api_complaints_list(self):
        res = self.client.get("/api/complaints?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_26_api_complaint_by_id(self):
        res = self.client.get("/api/complaints/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["id"], 1)

    def test_27_api_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total", data)
        self.assertIn("by_category", data)
        self.assertIn("active_categories", data)

    def test_28_api_departments_endpoint(self):
        res = self.client.get("/api/departments")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 6)
        self.assertIn("lead_engineer", data[0])

    def test_29_api_model_info_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("category_model", data)
        self.assertIn("priority_model", data)

    def test_30_api_export_report_endpoint(self):
        res = self.client.get("/api/export/report")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("report_title", data)
        self.assertIn("system_kpis", data)
        self.assertIn("department_load", data)
        self.assertIn("tickets_sample", data)

if __name__ == '__main__':
    unittest.main()
