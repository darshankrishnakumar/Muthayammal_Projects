"""
Automated QA Verification Suite for Project 29
AI-Based Sign Language Translation with Real-Time Speech and Text Generation
28 Comprehensive Unit & Integration Tests (100% Pass Rate Target)
"""

import os
import sys
import json
import unittest
import numpy as np
import torch

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "backend"))
DATA_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "data"))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import get_connection, verify_wal_status, get_all_vocabulary
from sign_engine import get_engine, SignSpatialClassifier, SignSequenceBiLSTM

class TestProject29SignLanguageSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.engine = get_engine()

    def test_01_health_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["port"], 5029)
        self.assertIn("models", data)
        self.assertIn("database", data)

    def test_02_models_loaded(self):
        self.assertIsNotNone(self.engine.spatial_model)
        self.assertIsNotNone(self.engine.seq_model)
        self.assertTrue(os.path.isfile(os.path.join(BACKEND_DIR, "sign_spatial_classifier_weights.pt")))
        self.assertTrue(os.path.isfile(os.path.join(BACKEND_DIR, "sign_sequence_bilstm_weights.pt")))

    def test_03_sqlite_wal_mode(self):
        wal = verify_wal_status()
        self.assertEqual(wal["journal_mode"], "WAL")
        self.assertTrue(wal["wal_enabled"])

    def test_04_database_seed_count(self):
        vocab = get_all_vocabulary()
        self.assertEqual(len(vocab), 38)
        self.assertIn("HELLO", vocab)
        self.assertIn("I LOVE YOU", vocab)
        self.assertIn("Z", vocab)

    def test_05_dictionary_endpoint(self):
        res = self.client.get("/api/dictionary")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 38)

    def test_06_dictionary_categories(self):
        vocab = get_all_vocabulary()
        cats = {v["category"] for v in vocab.values()}
        self.assertIn("Greeting", cats)
        self.assertIn("Emergency", cats)
        self.assertIn("Courtesy", cats)
        self.assertIn("Alphabet", cats)

    def test_07_recognize_hello(self):
        res = self.client.post("/api/recognize", json={"sign": "HELLO"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sign"], "HELLO")
        self.assertGreater(data["confidence_pct"], 80.0)
        self.assertEqual(len(data["landmarks_21"]), 21)

    def test_08_recognize_thank_you(self):
        res = self.client.post("/api/recognize", json={"sign": "THANK YOU"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sign"], "THANK YOU")
        self.assertGreater(data["confidence_pct"], 80.0)

    def test_09_recognize_emergency(self):
        res = self.client.post("/api/recognize", json={"sign": "EMERGENCY"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sign"], "EMERGENCY")
        self.assertEqual(data["category"], "Emergency")

    def test_10_recognize_alphabet_letters(self):
        for letter in ["A", "B", "C", "L", "Y"]:
            res = self.client.post("/api/recognize", json={"sign": letter})
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["sign"], letter)

    def test_11_top5_candidates(self):
        res = self.client.post("/api/recognize", json={"sign": "WATER"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        candidates = data["top_candidates"]
        self.assertEqual(len(candidates), 5)
        # Verify probabilities descending
        probs = [c["prob"] for c in candidates]
        self.assertTrue(all(probs[i] >= probs[i+1] for i in range(len(probs)-1)))

    def test_12_hand_landmarks_structure(self):
        res = self.client.post("/api/recognize", json={"sign": "DOCTOR"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        landmarks = data["landmarks_21"]
        self.assertEqual(len(landmarks), 21)
        for lm in landmarks:
            self.assertIn("id", lm)
            self.assertIn("name", lm)
            self.assertIn("x", lm)
            self.assertIn("y", lm)
            self.assertIn("z", lm)
            self.assertGreaterEqual(lm["x"], 0.0)
            self.assertLessEqual(lm["x"], 1.0)

    def test_13_raw_landmarks_inference(self):
        # Generate 21 dummy landmarks
        dummy_lms = [{"id": i, "name": f"J_{i}", "x": 0.5, "y": 0.5, "z": 0.0} for i in range(21)]
        res = self.client.post("/api/recognize", json={"landmarks": dummy_lms})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sign", data)
        self.assertIn("confidence_pct", data)

    def test_14_temporal_sequence_inference(self):
        # 16 frames of 63-dim features
        dummy_seq = np.random.normal(0.5, 0.1, (16, 63)).tolist()
        res = self.client.post("/api/translate-sequence", json={"sequence": dummy_seq})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("predicted_sign", data)
        self.assertIn("confidence_pct", data)
        self.assertIn("transition_completion", data)

    def test_15_history_retrieval(self):
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_16_history_limit_parameter(self):
        res = self.client.get("/api/history?limit=3")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertLessEqual(len(data), 3)

    def test_17_sentence_generation(self):
        res = self.client.get("/api/sentence")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sentence", data)
        self.assertIn("words", data)
        self.assertIn("word_count", data)

    def test_18_speech_logging(self):
        res = self.client.post("/api/speech/log", json={
            "text": "Hello, how are you?",
            "voice": "en-US",
            "rate": 1.0,
            "pitch": 1.0,
            "status": "COMPLETED"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "logged")

    def test_19_audit_log_endpoint(self):
        res = self.client.get("/api/audit-logs")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_20_metrics_endpoint(self):
        res = self.client.get("/api/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("metadata", data)
        self.assertIn("wal_status", data)

    def test_21_spatial_model_tensor_shape(self):
        dummy_in = torch.randn(1, 63)
        out = self.engine.spatial_model(dummy_in)
        self.assertEqual(out.shape, (1, 38))

    def test_22_bilstm_model_tensor_shapes(self):
        dummy_seq = torch.randn(1, 16, 63)
        logits, trans = self.engine.seq_model(dummy_seq)
        self.assertEqual(logits.shape, (1, 38))
        self.assertEqual(trans.shape, (1, 1))

    def test_23_coordinate_scalers_format(self):
        scalers_path = os.path.join(BACKEND_DIR, "landmark_scalers.json")
        self.assertTrue(os.path.isfile(scalers_path))
        with open(scalers_path, "r", encoding="utf-8") as f:
            sc = json.load(f)
        self.assertEqual(len(sc["mean"]), 63)
        self.assertEqual(len(sc["std"]), 63)

    def test_24_dataset_file_exists(self):
        csv_path = os.path.join(DATA_DIR, "sign_language_landmarks.csv")
        self.assertTrue(os.path.isfile(csv_path))
        import csv
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(len(header), 66) # sample_id, class_name, class_idx + 63 features
            rows = list(reader)
            self.assertEqual(len(rows), 5700)

    def test_25_latency_bounds(self):
        res = self.client.post("/api/recognize", json={"sign": "YES"})
        self.assertEqual(res.status_code, 200)
        latency = res.get_json()["latency_ms"]
        self.assertLess(latency, 100) # real-time threshold

    def test_26_static_file_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sign Language Translation", res.data)

    def test_27_404_handling(self):
        res = self.client.get("/invalid_nonexistent_endpoint_xyz")
        self.assertEqual(res.status_code, 404)

    def test_28_db_persistence_integrity(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM translation_sessions")
        count_before = cursor.fetchone()[0]
        conn.close()

        # Perform recognition
        self.client.post("/api/recognize", json={"sign": "NO"})

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM translation_sessions")
        count_after = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count_after, count_before + 1)

if __name__ == "__main__":
    unittest.main()
