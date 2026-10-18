import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestSignAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_vocab(self):
        res = self.client.get("/api/translation/vocabulary")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["count"], 5)

    def test_predict(self):
        res = self.client.post("/api/translation/predict", json={"gesture_index": 0})
        self.assertEqual(res.status_code, 200)
        self.assertIn("gloss", res.json())
        self.assertIn("spoken_sentence", res.json())

if __name__ == "__main__":
    unittest.main()
