import os
import sys
import json
import unittest
import numpy as np
import torch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
from ser_model import ser_engine, MultilingualSERNet, EMOTIONS
from app import app

class TestSpeechEmotionRecognitionSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        cls.client = app.test_client()
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # ─── 1. NEURAL NETWORK ARCHITECTURE & SERIALIZATION TESTS ───

    def test_ser_model_architecture(self):
        """Verify 1D-CNN + BiLSTM + Attention model architecture and parameter shapes."""
        model = MultilingualSERNet(in_features=40, num_classes=7)
        self.assertEqual(model.conv1.in_channels, 1)
        self.assertEqual(model.conv1.out_channels, 64)
        self.assertEqual(model.conv2.out_channels, 128)
        self.assertEqual(model.bilstm.hidden_size, 64)
        self.assertTrue(model.bilstm.bidirectional)
        self.assertEqual(model.classifier.out_features, 7)
        self.assertEqual(model.va_regressor.out_features, 2)

    def test_ser_weights_file_exists(self):
        """Verify serialized PyTorch model weights file exists and is non-empty."""
        weights_path = os.path.join(BACKEND_DIR, "ser_model_weights.pt")
        self.assertTrue(os.path.isfile(weights_path), "ser_model_weights.pt must exist")
        self.assertGreater(os.path.getsize(weights_path), 50000)

    def test_ser_metadata_json_exists(self):
        """Verify SER model metadata JSON exists and contains expected schema fields."""
        meta_path = os.path.join(BACKEND_DIR, "ser_model_metadata.json")
        self.assertTrue(os.path.isfile(meta_path), "ser_model_metadata.json must exist")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIn("model_architecture", meta)
        self.assertIn("classes", meta)
        self.assertIn("metrics", meta)
        self.assertEqual(meta["input_features"], 40)
        self.assertEqual(len(meta["classes"]), 7)

    def test_ser_metadata_accuracy_threshold(self):
        """Verify trained model achieves collegiate-grade classification accuracy >= 90%."""
        with open(os.path.join(BACKEND_DIR, "ser_model_metadata.json"), "r") as f:
            meta = json.load(f)
        acc = meta["metrics"]["test_accuracy"]
        f1 = meta["metrics"]["macro_f1"]
        self.assertGreaterEqual(acc, 0.90)
        self.assertGreaterEqual(f1, 0.90)

    def test_ser_forward_pass_shape(self):
        """Verify forward pass output dimensions for batch size 2."""
        dummy_input = torch.randn(2, 40)
        with torch.no_grad():
            logits, va, feat = ser_engine.model(dummy_input)
        self.assertEqual(logits.shape, (2, 7))
        self.assertEqual(va.shape, (2, 2))
        self.assertEqual(feat.shape, (2, 64))

    def test_ser_valence_arousal_bounds(self):
        """Verify Valence and Arousal coordinates remain within valid [-1.0, 1.0] range."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'happy', 'language': 'English'})
        self.assertGreaterEqual(res['valence'], -1.0)
        self.assertLessEqual(res['valence'], 1.0)
        self.assertGreaterEqual(res['arousal'], -1.0)
        self.assertLessEqual(res['arousal'], 1.0)

    def test_ser_probabilities_sum_to_one(self):
        """Verify posterior probability distribution across 7 emotions sums to 1.0."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'surprise', 'language': 'Spanish'})
        dist = res['emotion_distribution']
        total_p = sum(dist.values())
        self.assertAlmostEqual(total_p, 1.0, delta=0.05)

    def test_ser_happy_emotion_prediction(self):
        """Verify Happy preset produces high-confidence happy verdict with positive valence."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'happy', 'language': 'English'})
        self.assertEqual(res['emotion'], 'happy')
        self.assertGreater(res['valence'], 0.3)
        self.assertGreaterEqual(res['confidence'], 0.80)

    def test_ser_angry_emotion_prediction(self):
        """Verify Angry preset produces high-confidence angry verdict with negative valence and high arousal."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'angry', 'language': 'German'})
        self.assertEqual(res['emotion'], 'angry')
        self.assertLess(res['valence'], -0.3)
        self.assertGreater(res['arousal'], 0.4)

    def test_ser_fear_emotion_prediction(self):
        """Verify Fear preset produces high-confidence fear verdict with high pitch."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'fear', 'language': 'Hindi'})
        self.assertEqual(res['emotion'], 'fear')
        self.assertGreater(res['features']['pitch_f0_hz'], 220.0)

    def test_ser_sad_emotion_prediction(self):
        """Verify Sad preset produces negative valence and low energy."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'sad', 'language': 'Tamil'})
        self.assertEqual(res['emotion'], 'sad')
        self.assertLess(res['valence'], -0.3)
        self.assertLess(res['features']['rms_energy_db'], 0.45)

    def test_ser_neutral_emotion_prediction(self):
        """Verify Neutral preset produces near-zero valence."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'neutral', 'language': 'French'})
        self.assertEqual(res['emotion'], 'neutral')
        self.assertAlmostEqual(res['valence'], 0.0, delta=0.35)

    def test_ser_surprise_emotion_prediction(self):
        """Verify Surprise preset produces high arousal."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'surprise', 'language': 'Mandarin'})
        self.assertEqual(res['emotion'], 'surprise')
        self.assertGreater(res['arousal'], 0.3)

    def test_ser_disgust_emotion_prediction(self):
        """Verify Disgust preset produces negative valence."""
        res = ser_engine.predict_audio_features({'preset_emotion': 'disgust', 'language': 'Japanese'})
        self.assertEqual(res['emotion'], 'disgust')
        self.assertLess(res['valence'], -0.3)

    def test_ser_mfcc_coefficients_count(self):
        """Verify 13 MFCC spectral coefficients are returned in features."""
        res = ser_engine.predict_audio_features({'language': 'English'})
        mfccs = res['features']['mfcc_coefficients']
        self.assertEqual(len(mfccs), 13)

    # ─── 2. SQLITE RELATIONAL PERSISTENCE TESTS ───

    def test_sqlite_database_tables_exist(self):
        """Verify all mandatory tables exist in SQLite speech_emotion.db."""
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()
        for expected in ["audio_sessions", "emotion_benchmarks", "language_stats", "system_audit"]:
            self.assertIn(expected, tables)

    def test_sqlite_benchmarks_seeded(self):
        """Verify all 7 emotions are seeded in emotion_benchmarks table."""
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emotion_benchmarks")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 7)

    def test_sqlite_languages_seeded(self):
        """Verify all 8 multilingual targets are seeded in language_stats table."""
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM language_stats")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 8)

    def test_sqlite_sessions_seeded(self):
        """Verify initial audio sessions are pre-seeded."""
        sessions = database.get_recent_sessions(limit=50)
        self.assertGreaterEqual(len(sessions), 8)

    def test_sqlite_save_audio_session(self):
        """Verify save_audio_session inserts record and updates emotion benchmark count."""
        sample_data = ser_engine.predict_audio_features({'preset_emotion': 'happy', 'language': 'English'})
        sample_data['note'] = 'Unit test audio session'
        sess_id = database.save_audio_session(sample_data)
        self.assertIsNotNone(sess_id)
        self.assertGreater(sess_id, 0)

    def test_sqlite_audit_logging(self):
        """Verify system audit trail logs audio classification events."""
        logs = database.get_audit_logs(limit=10)
        self.assertGreater(len(logs), 0)
        self.assertTrue(any("AUDIO_CLASSIFICATION" in log["event_type"] or "DATABASE_INIT" in log["event_type"] for log in logs))

    # ─── 3. REST API ENDPOINT TESTS ───

    def test_api_health_endpoint(self):
        """GET /api/health should return 200 with service health and model metadata."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("1D-CNN", data["architecture"])
        self.assertEqual(data["supported_emotions"], 7)

    def test_api_recognize_nested_payload(self):
        """POST /api/recognize with nested audio_info payload returns 200 with emotion and features."""
        payload = {
            "audio_info": {
                "language": "English",
                "preset_emotion": "happy",
                "duration": 4.5
            },
            "note": "Nested payload test"
        }
        res = self.client.post("/api/recognize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["emotion"], "happy")
        self.assertIn("valence", data)
        self.assertIn("arousal", data)
        self.assertIn("features", data)

    def test_api_recognize_flat_payload(self):
        """POST /api/recognize with flat payload (for legacy audit) returns 200 with emotion."""
        payload = {"language": "en", "preset_emotion": "happy"}
        res = self.client.post("/api/recognize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("emotion", data)
        self.assertEqual(data["emotion"], "happy")

    def test_api_history_endpoint(self):
        """GET /api/history returns 200 and list of recent sessions."""
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        sessions = res.get_json()
        self.assertIsInstance(sessions, list)
        self.assertGreater(len(sessions), 0)

    def test_api_languages_endpoint(self):
        """GET /api/languages returns 200 and 8 supported languages."""
        res = self.client.get("/api/languages")
        self.assertEqual(res.status_code, 200)
        langs = res.get_json()
        self.assertEqual(len(langs), 8)

    def test_api_stats_endpoint(self):
        """GET /api/stats returns 200 with total_samples and supported_emotions."""
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertIn("total_samples", stats)
        self.assertIn("emotion_counts", stats)
        self.assertIn("avg_confidence_pct", stats)

    def test_api_model_info_endpoint(self):
        """GET /api/model/info returns 200 with 40-dim feature breakdown."""
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        info = res.get_json()
        self.assertEqual(info["input_dimension"], 40)
        self.assertIn("Bi-LSTM", info["architecture"])

    def test_api_audit_logs_endpoint(self):
        """GET /api/audit/logs returns 200 with audit events."""
        res = self.client.get("/api/audit/logs")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)

    # ─── 4. DELIVERABLES VERIFICATION TESTS ───

    def test_deliverables_verification(self):
        """Verify all required student capstone deliverables exist."""
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

if __name__ == "__main__":
    unittest.main()
