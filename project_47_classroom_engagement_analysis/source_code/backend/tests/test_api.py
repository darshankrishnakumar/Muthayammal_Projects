import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestEngagementAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_timeline(self):
        res = self.client.get("/api/engagement/timeline")
        self.assertEqual(res.status_code, 200)
        self.assertIn("snapshots", res.json())

    def test_analyze(self):
        res = self.client.post("/api/engagement/analyze", json={
            "attentive_pct": 82.0,
            "bored_pct": 8.0,
            "distracted_pct": 6.0,
            "drowsy_pct": 4.0
        })
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["metrics"]["mean_engagement_score"], 70.0)

if __name__ == "__main__":
    unittest.main()
