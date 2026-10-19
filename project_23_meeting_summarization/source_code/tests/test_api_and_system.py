"""
Comprehensive Automated QA and System Test Suite for PROJECT-023:
AI Meeting Summarization & Action-Item Extraction Engine.

Covers:
- Model artifact presence and validation
- TF-IDF Vectorization & vocabulary checks
- Dialogue act classification (ACTION_ITEM, DECISION, DISCUSSION, GENERAL)
- Priority classification (Critical, High, Medium, Low)
- TextRank sentence centrality and extractive summarization
- Speaker turn parsing and word count accounting
- Assignee and deadline resolution
- Relational SQLite transactional persistence and CRUD operations
- Action item lifecycle updates (OPEN -> COMPLETED)
- REST API endpoint contracts and error handling
"""

import unittest
import os
import sys
import json

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "backend"))

sys.path.insert(0, BACKEND_DIR)
import database
from app import app, parse_meeting_transcript, compute_textrank_centrality

class TestProject023System(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        database.init_db()

    # ─── SECTION 1: MODEL ARTIFACTS & METADATA TESTS ─────────────────────────

    def test_01_model_artifacts_exist(self):
        vec_path = os.path.join(BACKEND_DIR, "dialogue_act_vectorizer.joblib")
        act_path = os.path.join(BACKEND_DIR, "dialogue_act_classifier.joblib")
        prio_path = os.path.join(BACKEND_DIR, "task_priority_classifier.joblib")
        meta_path = os.path.join(BACKEND_DIR, "model_metadata.json")

        self.assertTrue(os.path.isfile(vec_path), "Dialogue act vectorizer must exist")
        self.assertTrue(os.path.isfile(act_path), "Dialogue act classifier must exist")
        self.assertTrue(os.path.isfile(prio_path), "Priority classifier must exist")
        self.assertTrue(os.path.isfile(meta_path), "Model metadata JSON must exist")

    def test_02_model_metadata_structure(self):
        meta_path = os.path.join(BACKEND_DIR, "model_metadata.json")
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        self.assertIn("dialogue_act_model", meta)
        self.assertIn("priority_model", meta)
        self.assertGreaterEqual(meta["dialogue_act_model"]["accuracy"], 0.85)
        self.assertGreater(meta.get("vocab_size", 0), 200)

    def test_03_vectorizer_transformation(self):
        import joblib
        vec = joblib.load(os.path.join(BACKEND_DIR, "dialogue_act_vectorizer.joblib"))
        X = vec.transform(["I will deploy the canary release to Kubernetes by Friday"])
        self.assertEqual(X.shape[0], 1)
        self.assertGreater(X.nnz, 0)

    def test_04_dialogue_act_classes(self):
        import joblib
        model = joblib.load(os.path.join(BACKEND_DIR, "dialogue_act_classifier.joblib"))
        expected = {'ACTION_ITEM', 'DECISION', 'DISCUSSION', 'GENERAL_STATEMENT'}
        self.assertEqual(set(model.classes_), expected)

    def test_05_priority_classes(self):
        import joblib
        model = joblib.load(os.path.join(BACKEND_DIR, "task_priority_classifier.joblib"))
        self.assertTrue({'Critical', 'High', 'Medium', 'Low'}.issubset(set(model.classes_)))

    # ─── SECTION 2: NLP EXTRACTION & SUMMARIZATION TESTS ─────────────────────

    def test_06_textrank_centrality_calculation(self):
        sents = [
            "We discussed the migration to Kafka event streaming.",
            "Kafka dropped latency from 420ms to 48ms.",
            "We agreed to adopt Kafka across all services."
        ]
        scores = compute_textrank_centrality(sents)
        self.assertEqual(len(scores), len(sents))
        self.assertAlmostEqual(sum(scores), 1.0, places=2)

    def test_07_action_item_extraction(self):
        transcript = "[Elena (DevOps)]: I will deploy the canary release v2.4 to the staging cluster by Friday."
        res = parse_meeting_transcript(transcript, "DevOps Sync")
        self.assertGreater(len(res['action_items']), 0)
        action = res['action_items'][0]
        self.assertIn("canary", action['task'].lower())
        self.assertEqual(action['assignee'], "Elena (DevOps)")
        self.assertEqual(action['deadline'], "Friday 5 PM")

    def test_08_decision_extraction(self):
        transcript = "[Marcus]: We decided to approve Kafka as our standard messaging backbone."
        res = parse_meeting_transcript(transcript, "Architecture Review")
        self.assertGreater(len(res['decisions']), 0)
        self.assertIn("Kafka", res['decisions'][0])

    def test_09_executive_summary_generation(self):
        transcript = """[Sarah]: Welcome team to our sprint review.
[Marcus]: I will optimize the database index scan by tomorrow morning.
[Elena]: We decided to automate zero-downtime certificate renewals."""
        res = parse_meeting_transcript(transcript, "Sprint Review")
        self.assertIn("executive_summary", res)
        self.assertTrue(len(res['executive_summary']) > 30)

    def test_10_speaker_word_counts(self):
        transcript = """[Alice]: One two three four.
[Bob]: Five six seven."""
        res = parse_meeting_transcript(transcript, "Word Count Test")
        self.assertEqual(res['speaker_stats']['Alice'], 4)
        self.assertEqual(res['speaker_stats']['Bob'], 3)
        self.assertEqual(res['word_count'], 7)

    def test_11_engagement_and_sentiment_metrics(self):
        transcript = """[Alice]: Great progress everyone, excellent results.
[Bob]: Thanks Alice, the performance benchmarks look optimal."""
        res = parse_meeting_transcript(transcript, "Metrics Test")
        self.assertTrue(50.0 <= res['engagement_score'] <= 100.0)
        self.assertTrue(0.0 <= res['sentiment_index'] <= 1.0)
        self.assertGreaterEqual(res['sentiment_index'], 0.60)

    # ─── SECTION 3: RELATIONAL SQLITE DATABASE TESTS ──────────────────────────

    def test_12_database_tables_exist(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for t in ['meetings', 'action_items', 'decisions', 'system_audit']:
            self.assertIn(t, tables)

    def test_13_database_add_and_retrieve_meeting(self):
        meeting_data = {
            'title': 'Test QA Session',
            'timestamp': '2026-10-20 02:00:00',
            'transcript': '[Test User]: I will run QA automated verification by today.',
            'executive_summary': 'QA automated verification test session executed.',
            'summary_bullets': ['Executed QA verification.'],
            'word_count': 10,
            'duration_est_mins': 2.0,
            'compression_ratio_pct': 45.0,
            'sentiment_index': 0.80,
            'engagement_score': 90.0,
            'speaker_stats': {'Test User': 10},
            'action_items': [{
                'task': 'Run QA verification',
                'assignee': 'Test User',
                'priority': 'High',
                'category': 'Testing',
                'deadline': 'Today EOD',
                'status': 'OPEN'
            }],
            'decisions': ['Approved QA test execution.']
        }
        m_id = database.add_meeting(meeting_data)
        self.assertIsInstance(m_id, int)
        self.assertGreater(m_id, 0)

        retrieved = database.get_meeting_by_id(m_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], meeting_data['title'])
        self.assertEqual(len(retrieved['action_items']), 1)
        self.assertEqual(retrieved['action_items'][0]['task'], 'Run QA verification')

    def test_14_database_action_status_update(self):
        meetings = database.get_meetings(limit=1)
        self.assertGreater(len(meetings), 0)
        actions = meetings[0]['action_items']
        self.assertGreater(len(actions), 0)
        act_id = actions[0]['id']

        ok = database.update_action_status(act_id, 'COMPLETED')
        self.assertTrue(ok)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM action_items WHERE id = ?", (act_id,))
        status = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(status, 'COMPLETED')

    def test_15_database_stats_aggregation(self):
        stats = database.get_stats()
        self.assertIn("total_meetings", stats)
        self.assertIn("total_action_items", stats)
        self.assertIn("total_decisions_logged", stats)
        self.assertIn("avg_engagement_pct", stats)
        self.assertGreater(stats['total_meetings'], 0)

    def test_16_database_audit_trail_logging(self):
        logs = database.get_audit_logs(limit=10)
        self.assertGreater(len(logs), 0)
        self.assertIn("event_type", logs[0])
        self.assertIn("outcome", logs[0])

    # ─── SECTION 4: REST API ENDPOINTS TESTS ─────────────────────────────────

    def test_17_api_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("dialogue_act_accuracy_pct", data)

    def test_18_api_summarize_success(self):
        res = self.client.post("/api/summarize", json={
            "title": "API Sprint Review",
            "transcript": "[Marcus]: I will finish the database indexing before Friday.\n[Sarah]: We decided to approve the schema changes."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("id", data)
        self.assertIn("executive_summary", data)
        self.assertIn("action_items", data)
        self.assertIn("decisions", data)

    def test_19_api_summarize_empty_error(self):
        res = self.client.post("/api/summarize", json={"transcript": ""})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_20_api_meetings_list(self):
        res = self.client.get("/api/meetings?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_21_api_meeting_by_id(self):
        res = self.client.get("/api/meetings/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["id"], 1)

    def test_22_api_meeting_by_id_not_found(self):
        res = self.client.get("/api/meetings/99999")
        self.assertEqual(res.status_code, 404)

    def test_23_api_action_status_update(self):
        res = self.client.post("/api/actions/1/status", json={"status": "IN_PROGRESS"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))

    def test_24_api_stats(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_meetings", data)
        self.assertIn("total_action_items", data)

    def test_25_api_model_info(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("dialogue_act_model", data)
        self.assertIn("priority_model", data)

    def test_26_api_audit_logs(self):
        res = self.client.get("/api/audit")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_27_api_export_minutes(self):
        res = self.client.get("/api/export/minutes/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("markdown_minutes", data)
        self.assertIn("Executive Meeting Minutes", data["markdown_minutes"])

if __name__ == '__main__':
    unittest.main()
